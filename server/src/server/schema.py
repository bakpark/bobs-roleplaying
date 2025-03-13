from pydantic import BaseModel

class SimpleMessageRequest(BaseModel):
    message: str
    session_id: str
