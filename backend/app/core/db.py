from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine, SQLModel

sqlite_name = "${POSTGRES_DB}"
sqlite_url = f"sqlite:///{sqlite_name}"

engine = create_engine(sqlite_url)

def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

# Registramos la dependencia de la sesión
SessionDep = Annotated[Session, Depends(get_session)]