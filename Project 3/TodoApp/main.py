from fastapi import FastAPI
import models
from database import engine

app = FastAPI()

# create the tables in the database based on the models defined in models.py
models.Base.metadata.create_all(bind=engine) 