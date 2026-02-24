from pydantic import BaseModel
from typing import List, Optional

class SourceMetadata(BaseModel):
    source: str
    source_type: str  # 'vector', 'graph', 'csv'

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata] = []