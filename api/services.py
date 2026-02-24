import httpx
import os

class OrchestratorClient:
    def __init__(self):
        # Defaults to local orchestrator port if env var is missing
        self.base_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:8002")
        self.timeout = 60.0 # RAG pipelines can be slow

    async def send_query(self, query: str) -> dict:
        """Sends the validated query to the LangGraph orchestration service."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/orchestrate",
                json={"query": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()