
import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker


# Use a separate database when DATABASE_URL is provided
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./yottaflex.db"
)


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Enable foreign key enforcement in SQLite
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):

    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()
