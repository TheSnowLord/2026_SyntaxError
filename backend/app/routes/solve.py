from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4

from app.database.db import get_session
from app.database.models import AgentSession

router = APIRouter()


class SolveRequest(BaseModel):
    goal: str


@router.post("/solve")
def solve(request: SolveRequest):

    session = get_session()

    session_id = str(uuid4())

    new_session = AgentSession(
        session_id=session_id,
        goal=request.goal,
        status="processing",
        current_agent="Planner",
        progress=0
    )

    session.add(new_session)
    session.commit()
    session.refresh(new_session)

    return {
        "session_id": session_id,
        "status": "processing",
        "current_agent": "Planner",
        "progress": 0,
        "message": "Task accepted."
    }