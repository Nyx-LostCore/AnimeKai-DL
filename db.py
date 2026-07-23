from typing import Generator
import os

from sqlmodel import (
    SQLModel,
    Session,
    create_engine,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./animekaidl.db",
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session