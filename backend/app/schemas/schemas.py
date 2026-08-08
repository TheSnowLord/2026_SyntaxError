from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SolveRequest(BaseModel):
    goal: str = Field(..., description="The complex goal for AgentForge AI to decompose and solve", min_length=1)


class SolveResponse(BaseModel):
    session_id: str
    status: str
    current_agent: str
    progress: int
    message: str
    result: Optional[str] = None



class SessionStatusResponse(BaseModel):
    session_id: str
    goal: str
    status: str
    current_agent: str
    progress: int
    result: Optional[str] = None
    created_at: datetime


class SessionListResponse(BaseModel):
    total: int
    sessions: List[SessionStatusResponse]


class ErrorResponse(BaseModel):
    detail: str

