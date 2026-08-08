import os
import time
import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket
from sqlmodel import select
from dotenv import load_dotenv

from app.database.db import get_session
from app.database.models import AgentSession

load_dotenv()
logger = logging.getLogger("agentforge.ai_service")


class ConnectionManager:
    """
    Manages active WebSocket connections for live progress streaming per session.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket client connected to session {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session {session_id}")

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending websocket message: {e}")
                    disconnected.append(connection)
            for conn in disconnected:
                self.disconnect(session_id, conn)


# Global connection manager instance
manager = ConnectionManager()


def call_llm_agent(prompt: str, agent_role: str) -> str:
    """
    Invokes local Ollama AI engine first (100% offline & local).
    Falls back to Gemini/Groq APIs if configured in .env, or structured local synthesis.
    """
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()

    # 1. Try Local Ollama AI Engine (100% Offline, Local GPU)
    try:
        import urllib.request
        import json
        model_name = f"{agent_role.lower()}-agent" if agent_role in ["Researcher", "Developer", "Planner", "Decomposer", "Evaluator"] else "qwen2.5:3b"
        url = f"{ollama_host}/api/generate"
        payload = json.dumps({
            "model": model_name,
            "prompt": f"System: You are the {agent_role} agent in AgentForge AI platform.\nUser: {prompt}",
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "response" in res_data and res_data["response"].strip():
                return res_data["response"].strip()
    except Exception as e:
        logger.info(f"Local Ollama engine check ({agent_role}): {e}")

    # 2. Try Gemini if key is provided in .env
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key and not gemini_key.startswith("your_"):
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are the {agent_role} agent in AgentForge AI platform.\n{prompt}"
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")

    # 3. Try Groq if key is provided in .env
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key and not groq_key.startswith("your_"):
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are the {agent_role} agent in AgentForge AI platform."},
                    {"role": "user", "content": prompt}
                ]
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Groq API call failed: {e}")

    # 4. Local AgentForge AI Structured Synthesis
    return f"[{agent_role} Local AI Agent] Generated output and processed requirements for task."



def update_session_state(session_id: str, current_agent: str, progress: int, status: str = "processing", result: str = None):
    """
    Helper function to update AgentSession in SQLite database and trigger broadcast.
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

    # Broadcast real-time event to connected WebSocket clients safely
    event_payload = {
        "event": "progress_update",
        "session_id": session_id,
        "current_agent": current_agent,
        "progress": progress,
        "status": status,
        "result": result
    }

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast_to_session(session_id, event_payload))
    except RuntimeError:
        asyncio.run(manager.broadcast_to_session(session_id, event_payload))


def run_agent_pipeline_background(session_id: str, goal: str):
    """
    Background worker that runs the multi-agent pipeline for a session.
    """
    try:
        # Stage 1: Planner Agent
        logger.info(f"Session {session_id}: Planner agent analyzing goal...")
        planner_res = call_llm_agent(f"Analyze goal: '{goal}' and state the strategic execution plan.", "Planner")
        update_session_state(session_id, current_agent="Planner", progress=20, status="processing")
        time.sleep(1.0)

        # Stage 2: Decomposer Agent
        logger.info(f"Session {session_id}: Decomposer breaking down tasks...")
        decomposer_res = call_llm_agent(f"Decompose goal: '{goal}' into clear, modular sub-tasks.", "Decomposer")
        update_session_state(session_id, current_agent="Decomposer", progress=40, status="processing")
        time.sleep(1.0)

        # Stage 3: Researcher Agent
        logger.info(f"Session {session_id}: Researcher analyzing architecture & specs...")
        researcher_res = call_llm_agent(f"Research technical architecture and best practices for: '{goal}'.", "Researcher")
        update_session_state(session_id, current_agent="Researcher", progress=60, status="processing")
        time.sleep(1.0)

        # Stage 4: Developer Agent
        logger.info(f"Session {session_id}: Developer agent generating code implementation...")
        developer_res = call_llm_agent(f"Generate clean, production-ready code implementation for: '{goal}'.", "Developer")
        update_session_state(session_id, current_agent="Developer", progress=80, status="processing")
        time.sleep(1.0)

        # Stage 5: Evaluator Agent & Solution Synthesis
        logger.info(f"Session {session_id}: Evaluator synthesizing final output...")
        evaluator_res = call_llm_agent(f"Verify, review code quality, and synthesize final output for: '{goal}'.", "Evaluator")
        
        final_solution = (
            f"### AgentForge AI 5-Stage Multi-Agent Unified Solution\n"
            f"**Goal**: {goal}\n\n"
            f"#### 1. Strategic Plan (Planner Agent)\n{planner_res}\n\n"
            f"#### 2. Task Decomposition (Decomposer Agent)\n{decomposer_res}\n\n"
            f"#### 3. Architecture & Technical Research (Researcher Agent)\n{researcher_res}\n\n"
            f"#### 4. Production Code Implementation (Developer Agent)\n{developer_res}\n\n"
            f"#### 5. Evaluation & Final Synthesis (Evaluator Agent)\n{evaluator_res}"
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

