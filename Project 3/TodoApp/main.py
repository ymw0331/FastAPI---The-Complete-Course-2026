from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, HTTPException, Path, status
# Depends = DI (Dependency Injection) in FastAPI, it allows you to declare dependencies that should be injected into your path operation functions. In this case, we are declaring a dependency on the database session, which will be provided by the get_db function. This allows us to easily access the database session in our path operation functions without having to manually create and manage the session each time.

import models
from models import Todos
from database import engine, SessionLocal

app = FastAPI()

# create the tables in the database based on the models defined in models.py
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    # this function on DB session as a dependency, which will be provided by the get_db function. The Annotated type hint is used to specify that the db parameter is of type Session and that it should be provided by the Depends function.
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")
