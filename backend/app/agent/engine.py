from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.security import verify_sql_safety, SQLSecurityValidationError
from app.database.session import execute_read_only_query
from app.agent.metadata import get_database_schema_context
from app.agent.prompts import SYSTEM_ANALYST_PROMPT
from app.agent.contracts import SQLGenerationDraft, FinalAgentPayload, ChartSpecification

def run_analytics_agent_loop(user_query: str, max_retries: int = 3) -> FinalAgentPayload:
    """
    Orchestrates the entire text-to-SQL generation, validation, and self-correction loop.
    """
    schema_context = get_database_schema_context()
    
    # 1. Initialize our localized strict Pydantic JSON parser
    json_parser = JsonOutputParser(pydantic_object=SQLGenerationDraft)
    
    # 2. Inject explicit format instructions directly into the prompt stream
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_ANALYST_PROMPT + "\n\n{format_instructions}"),
        ("human", "{input_query}")
    ])
    
    # 3. Clean DeepSeek Client Connection
    llm = ChatOpenAI(
        model="deepseek-chat", 
        temperature=0.0, 
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_API_BASE
    )
    
    # Pipe the raw response directly into the JSON interpreter block
    chain = prompt_template | llm | json_parser
    
    current_attempt = 0
    feedback_modifier = ""
    active_query_to_process = user_query

    while current_attempt < max_retries:
        try:
            current_attempt += 1
            
            if feedback_modifier:
                active_query_to_process = f"{user_query}\n\nPREVIOUS ATTEMPT FAILED:\n{feedback_modifier}"

            # Step A: Invoke the model passing format instructions generated automatically by LangChain
            parsed_json_dict = chain.invoke({
                "schema_context": schema_context,
                "input_query": active_query_to_process,
                "format_instructions": json_parser.get_format_instructions()
            })
            
            # Convert the cleanly parsed Python dictionary straight back into our strict Pydantic contract
            draft_output = SQLGenerationDraft.model_validate(parsed_json_dict)
            generated_sql = draft_output.sql_query
            
            # Step B: Guardrail Safety Scan
            verify_sql_safety(generated_sql)
            
            # Step C: Database Query Execution
            raw_dataset = execute_read_only_query(generated_sql)
            
            # Step D: Auxiliary Processing Chains
            visualization_config = determine_chart_mapping(llm, user_query, raw_dataset)
            insights_narrative = generate_insights_summary(llm, user_query, raw_dataset)

            return FinalAgentPayload(
                insights_narrative=insights_narrative,
                executed_sql=generated_sql,
                dataset=raw_dataset,
                visualization_config=visualization_config
            )

        except (SQLAlchemyError, SQLSecurityValidationError, Exception) as recoverable_error:
            print(f"[Loop Attempt {current_attempt} Failed]: {str(recoverable_error)}")
            feedback_modifier = (
                f"Your generated query failed validation rules.\n"
                f"Exception Logs: {str(recoverable_error)}\n"
                f"Please optimize, fix syntax, and rewrite a clean response object."
            )
            
    raise RuntimeError(f"Agent loop fatigue after {max_retries} failures. Last error: {feedback_modifier}")

def determine_chart_mapping(llm, original_query: str, dataset: list) -> ChartSpecification:
    if not dataset:
        return ChartSpecification(chart_type="table", x_axis_key="", y_axis_key="", chart_title="No Data Available")
        
    sample_row_keys = list(dataset[0].keys())
    
    # Set up our chart parser
    chart_parser = JsonOutputParser(pydantic_object=ChartSpecification)
    
    chart_prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze this dataset structure and determine the best chart schema to plot it. Available column keys: {keys}\n{format_instructions}"),
        ("human", "Original request: {query}")
    ])
    
    chart_chain = chart_prompt | llm | chart_parser
    
    parsed_chart_dict = chart_chain.invoke({
        "keys": str(sample_row_keys), 
        "query": original_query,
        "format_instructions": chart_parser.get_format_instructions()
    })
    
    return ChartSpecification.model_validate(parsed_chart_dict)

def generate_insights_summary(llm, original_query: str, dataset: list) -> str:
    """Helper method synthesizing raw list output into bulleted human observations."""
    if not dataset:
        return "No corresponding records were found matching your parameters inside the analytics tracking matrix."
        
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional business advisor. Summarize the key trends seen in this raw database output in 2-3 concise bullet points."),
        ("human", "User query: {query}\nRaw Data Matrix: {data}")
    ])
    
    summary_chain = summary_prompt | llm
    response = summary_chain.invoke({"query": original_query, "data": str(dataset[:10])}) # Send top 10 rows for brevity
    return response.content