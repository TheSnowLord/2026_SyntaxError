import time
import logging
from sqlmodel import select
from app.database.db import get_session
from app.database.models import AgentSession

logger = logging.getLogger("agentforge.ai_service")


def update_session_state(session_id: str, current_agent: str, progress: int, status: str = "processing", result: str = None):
    """
    Helper function to update AgentSession in SQLite database.
    """
    with get_session() as db:
        statement = select(AgentSession).where(AgentSession.session_id == session_id)
        session_obj = db.exec(statement).first()
        if session_obj:
            session_obj.current_agent = current_agent
            session_obj.progress = progress
            session_obj.status = status
            if result is not None:
                session_obj.result = result
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)


def run_agent_pipeline_background(session_id: str, goal: str):
    """
    Background worker that runs the multi-agent pipeline for a session.
    This provides a clean interface for the AI teammate (5050) to attach Gemini/Groq LLM logic.
    """
    try:
        # Stage 1: Planner Agent
        logger.info(f"Session {session_id}: Planner agent analyzing goal...")
        update_session_state(session_id, current_agent="Planner", progress=25, status="processing")
        time.sleep(1.5)

        # Stage 2: Task Decomposition Agent
        logger.info(f"Session {session_id}: Decomposer breaking down tasks...")
        update_session_state(session_id, current_agent="Decomposer", progress=50, status="processing")
        time.sleep(1.5)

        # Stage 3: Execution Agent
        logger.info(f"Session {session_id}: Executor running task sub-agents...")
        update_session_state(session_id, current_agent="Executor", progress=75, status="processing")
        time.sleep(1.5)

        # Stage 4: Evaluator & Final Synthesis
        logger.info(f"Session {session_id}: Evaluator synthesizing final output...")
        final_solution = (
            f"AgentForge AI Solution for: '{goal}'\n\n"
            f"1. Plan: Analyzed constraints and target requirements.\n"
            f"2. Decomposition: Subdivided work into backend, frontend, and AI tasks.\n"
            f"3. Execution: Generated required modules and integrations.\n"
            f"4. Evaluation: Solution verified and ready for deployment."
        )
        update_session_state(
            session_id,
            current_agent="Evaluator",
            progress=100,
            status="completed",
            result=final_solution
        )
        logger.info(f"Session {session_id}: Completed successfully.")

    except Exception as e:
        logger.error(f"Session {session_id} failed: {str(e)}")
        update_session_state(
            session_id,
            current_agent="Error",
            progress=0,
            status="failed",
            result=f"Execution error: {str(e)}"
        )
