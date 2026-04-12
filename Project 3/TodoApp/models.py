from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todos (Base):
    # specify the name of the table in the database
    __tablename__ = "todos" 

    # id column is the primary key and indexed for faster queries (indexable, increase performance)
    id = Column(Integer, primary_key=True, index=True) 
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False) 


