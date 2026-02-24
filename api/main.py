from fastapi import FastAPI, HTTPException
from models import ChatRequest, ChatResponse
from services import OrchestratorClient

app = FastAPI(title="TaxGPT API Gateway", version="1.0.0")
client = OrchestratorClient()

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives user queries and routes them to the LangGraph orchestrator.
    """
    try:
        # Delegate the actual HTTP call to the services layer (DRY)
        result = await client.send_query(request.query)
        return ChatResponse(answer=result["answer"], sources=result["sources"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}