from sqlmodel import SQLModel, create_engine, Session
from app.database.models import AgentSession

DATABASE_URL = "sqlite:///agentforge.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)