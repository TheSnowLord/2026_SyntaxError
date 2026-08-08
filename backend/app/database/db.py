from sqlmodel import SQLModel, create_engine, Session
from app.database.models import AgentSession

DATABASE_URL = "sqlite:///agentforge.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def create_db():
    SQLModel.metadata.create_all(engine)


# Ensure tables are created when module is loaded
create_db()


def get_session():
    return Session(engine)