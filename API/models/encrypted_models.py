from pydantic import BaseModel

class EncryptedRequest(BaseModel):
    data: str  # Encrypted JSON string

class EncryptedResponse(BaseModel):
    data: str  # Encrypted JSON string