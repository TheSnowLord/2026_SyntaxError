from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class AgentSession(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    session_id: str = Field(index=True, unique=True)

    goal: str

    status: str = Field(default="processing", index=True)

    current_agent: str = Field(default="Planner", index=True)

    progress: int = Field(default=0)

    result: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)