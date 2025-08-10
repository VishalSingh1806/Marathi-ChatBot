from pydantic import BaseModel
from typing import List, Optional

class QueryResponse(BaseModel):
    answer: str
    similar_questions: Optional[List[str]] = None
    session_id: str

class TranscribeResponse(BaseModel):
    transcript: str