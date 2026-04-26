from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from fastapi import FastAPI, Depends, HTTPException, Path, status

import models
from models import Todos
from database import engine, SessionLocal

app = FastAPI()

# creates all tables in the DB based on models.py (runs once on startup)
models.Base.metadata.create_all(bind=engine)


# yields a DB session per request, and closes it when the request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Depends: injects get_db() into each route so we don't manually manage the session
db_dependency = Annotated[Session, Depends(get_db)]


# Pydantic model: validates and parses the request body for create/update endpoints
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)  # must be 1–5
    complete: bool = False


# GET / — return all todos
@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()


# GET /todo/{todo_id} — return a single todo by ID, 404 if not found
# Path(gt=0) ensures todo_id must be a positive integer
@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


# POST /todo — create a new todo from the request body, returns 201 on success
# **todo_request.dict() unpacks the Pydantic model into keyword args (like JS spread: { ...obj })
@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()


# PUT /todo/{todo_id} — update an existing todo, returns 204 (no content) on success
@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_id: int, todo_request: TodoRequest):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # overwrite each field with the new values from the request
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
