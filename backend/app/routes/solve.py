from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect, status
from uuid import uuid4
from sqlmodel import select, desc

from app.database.db import get_session
from app.database.models import AgentSession
from app.schemas.schemas import SolveRequest, SolveResponse, SessionStatusResponse, SessionListResponse
from app.services.ai_service import run_agent_pipeline_background, manager

router = APIRouter(tags=["Solving & Sessions"])


@router.post("/solve", response_model=SolveResponse, status_code=status.HTTP_200_OK)
@router.post("/api/solve", response_model=SolveResponse, status_code=status.HTTP_200_OK)
def solve(request: SolveRequest, background_tasks: BackgroundTasks):
    if not request.goal or not request.goal.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal cannot be empty."
        )

    session_id = str(uuid4())

    with get_session() as db:
        new_session = AgentSession(
            session_id=session_id,
            goal=request.goal.strip(),
            status="processing",
            current_agent="Planner",
            progress=0
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

    # Launch background AI multi-agent processing pipeline
    background_tasks.add_task(run_agent_pipeline_background, session_id, request.goal.strip())

    return SolveResponse(
        session_id=session_id,
        status="processing",
        current_agent="Planner",
        progress=0,
        message="Task accepted and multi-agent workflow started."
    )




@router.get("/api/sessions", response_model=SessionListResponse)
def list_sessions():
    with get_session() as db:
        statement = select(AgentSession).order_by(desc(AgentSession.created_at)).limit(50)
        results = db.exec(statement).all()
        sessions = [
            SessionStatusResponse(
                session_id=s.session_id,
                goal=s.goal,
                status=s.status,
                current_agent=s.current_agent,
                progress=s.progress,
                result=s.result,
                created_at=s.created_at
            ) for s in results
        ]
        return SessionListResponse(total=len(sessions), sessions=sessions)


@router.get("/solve/{session_id}", response_model=SessionStatusResponse)
@router.get("/api/session/{session_id}", response_model=SessionStatusResponse)
def get_session_status(session_id: str):
    with get_session() as db:
        statement = select(AgentSession).where(AgentSession.session_id == session_id)
        session_obj = db.exec(statement).first()

        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID '{session_id}' not found."
            )

        return SessionStatusResponse(
            session_id=session_obj.session_id,
            goal=session_obj.goal,
            status=session_obj.status,
            current_agent=session_obj.current_agent,
            progress=session_obj.progress,
            result=session_obj.result,
            created_at=session_obj.created_at
        )


@router.websocket("/ws/solve/{session_id}")
@router.websocket("/ws/session/{session_id}")
async def websocket_session_stream(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        # Send initial session state upon connection
        with get_session() as db:
            statement = select(AgentSession).where(AgentSession.session_id == session_id)
            session_obj = db.exec(statement).first()
            if session_obj:
                await websocket.send_json({
                    "event": "initial_state",
                    "session_id": session_obj.session_id,
                    "goal": session_obj.goal,
                    "status": session_obj.status,
                    "current_agent": session_obj.current_agent,
                    "progress": session_obj.progress,
                    "result": session_obj.result
                })

        # Keep connection open for incoming pings or messages
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
