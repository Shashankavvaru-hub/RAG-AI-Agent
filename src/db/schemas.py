from pydantic import BaseModel
from typing import List

class Chat(BaseModel):
    id: int = 0
    name: str = "New Chat"
    
    def dict(self):
        return {"id": self.id, "name": self.name}

class Message(BaseModel):
    id: int
    type: str  # "user" or "agent"
    body: str
    reasoning_steps: List[dict] = []  
    class Config:
        orm_mode = True
    
    def dict(self):
        return {"id": self.id, "type": self.type, "body": self.body}
