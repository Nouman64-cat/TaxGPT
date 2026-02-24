from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import app as workflow_app
import traceback

server = FastAPI(title="LangGraph Orchestrator")

class OrchestrateRequest(BaseModel):
    query: str

@server.post("/orchestrate")
async def orchestrate(request: OrchestrateRequest):
    try:
        # 1. Initialize the state
        initial_state = {
            "query": request.query, 
            "route": "", 
            "context": [], 
            "answer": ""
        }
        
        # 2. Execute the LangGraph workflow
        final_state = workflow_app.invoke(initial_state)
        
        # 3. Return the payload to the API Gateway
        return {
            "answer": final_state.get("answer"),
            "sources": [{"source": "retrieved_data", "source_type": final_state.get("route")}]
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))