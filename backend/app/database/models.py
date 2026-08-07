from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class AgentSession(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    session_id: str = Field(index=True)

    goal: str

    status: str = "processing"

    current_agent: str = "Planner"

    progress: int = 0

    result: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)