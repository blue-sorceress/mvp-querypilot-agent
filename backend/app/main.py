from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent.engine import run_analytics_agent_loop
from app.agent.contracts import FinalAgentPayload
from app.core.security import SQLSecurityValidationError

# Initialize the main FastAPI application instance
app = FastAPI(
    title="MVP QueryPilot Analytics AI Agent",
    description="Natural language to SQL Engine equipped with guardrails and self-healing execution loops.",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS)
# This allows the future frontend (Vue.js/React) to seamlessly communicate with this API layer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    """The formal JSON schema incoming request layout from the web client."""
    prompt: str = Field(
        ..., 
        example="Show me the average platform engagement time grouped by student risk status.",
        description="The natural language data query requested by the stakeholder."
    )

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Simple connection verification heartbeat endpoint."""
    return {"status": "healthy", "service": "analytics-agent-backend"}

@app.post(
    "/api/v1/analytics/query", 
    response_model=FinalAgentPayload, 
    status_code=status.HTTP_200_OK,
    summary="Process natural language analytics requests"
)
def process_analytics_request(payload: QueryRequest):
    """
    Accepts user prompts, orchestrates autonomous text-to-SQL translation,
    runs safety checks, resolves errors via self-healing retries, and returns structured chart data.
    """
    # Defensive programming: Ensure the input prompt isn't empty or malicious garbage text
    clean_prompt = payload.prompt.strip()
    if not clean_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided query prompt cannot be empty."
        )
        
    try:
        # Invoke our core engine loop
        agent_response_packet = run_analytics_agent_loop(user_query=clean_prompt)
        return agent_response_packet

    except SQLSecurityValidationError as security_error:
        # Explicitly catch security rule violations and map to a 403 Forbidden status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security Intercept: {str(security_error)}"
        )
        
    except Exception as runtime_error:
        # Fallback layer catching absolute engine fatigue or terminal system breakdowns
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"The agent engine was unable to resolve your request cleanly. Error: {str(runtime_error)}"
        )