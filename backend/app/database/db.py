from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from app.database.models import AgentSession

DATABASE_URL = "sqlite:///agentforge.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False, "timeout": 30}
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Configures SQLite WAL mode and performance optimizations for concurrent multi-agent access.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


def create_db():
    SQLModel.metadata.create_all(engine)


# Ensure tables are created when module is loaded
create_db()


def get_session():
    return Session(engine)
