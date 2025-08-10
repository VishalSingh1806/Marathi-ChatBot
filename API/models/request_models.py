from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    csrf_token: Optional[str] = None

class TranscribeRequest(BaseModel):
    csrf_token: Optional[str] = None

class CSRFTokenResponse(BaseModel):
    csrf_token: str
    session_id: str