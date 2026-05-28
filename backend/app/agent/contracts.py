from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field

class SQLGenerationDraft(BaseModel):
    """The raw structure the LLM must generate during its thinking phase."""
    thought_process: str = Field(
        description="Internal monologue detailing why these columns and tables were selected."
    )
    sql_query: str = Field(
        description="The clean, executable SQL string. Must include an explicit LIMIT if not already bounded."
    )

class ChartSpecification(BaseModel):
    """Tells the frontend exactly how to dynamically map the database rows into charts."""
    chart_type: Literal["bar", "line", "pie", "table"] = Field(
        description="The exact visualization layout choice best matching the dataset shape."
    )
    x_axis_key: str = Field(
        description="The exact dictionary key string from the data row array to use for the X axis."
    )
    y_axis_key: str = Field(
        description="The exact dictionary key string from the data row array to use for the Y axis."
    )
    chart_title: str = Field(
        description="A clear, short title summarizing the visual graph context."
    )

class FinalAgentPayload(BaseModel):
    """The production data packet delivered straight down the FastAPI route to your web UI."""
    insights_narrative: str = Field(
        description="A concise human-readable summary analyzing the trends discovered in the resulting rows."
    )
    executed_sql: str = Field(
        description="The verified, secure SQL command that successfully executed against the database."
    )
    dataset: List[Dict[str, Any]] = Field(
        description="The raw array of row objects parsed straight from the database engine execution."
    )
    visualization_config: Optional[ChartSpecification] = Field(
        default=None,
        description="Visual mapping layout instructions if the data contains plottable metrics."
    )