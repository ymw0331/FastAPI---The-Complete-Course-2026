from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    id: Optional[int] = None # user does not provide id (can be integer or None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)  # 0 - 5


BOOKS = [
    Book(
        1,
        "Computer Science Pro",
        "Wayney Yong",
        "A comprehensive guide to computer science.",
        5,
    ),
    Book(
        2,
        "Advanced Python",
        "Wayney Yong",
        "An advanced guide to Python programming.",
        5,
    ),
    Book(
        3,
        "Data Science Essentials",
        "Wayney Yong",
        "Essential concepts in data science.",
        5,
    ),
    Book(4, "HP1", "Author 1", "Book Description 1.", 2),
    Book(5, "HP2", "Author 2", "Book Description 1.", 3),
    Book(6, "HP3", "Author 3", "Book Description 1.", 1),
]


@app.get("/books/")
async def read_all_books():
    return BOOKS


@app.post("/create-book")
async def create_book(book_request: BookRequest):
    # new_book = Book(**book_request.dict()) # Pydantic1
    new_book = Book(**book_request.model_dump())  # Pydantic2

    BOOKS.append(find_book_id(new_book))


# normal function to add id to the book
def find_book_id(book: Book):

    # ternary operator
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1 # get last book id and add 1
    # else:
    #     book.id = 1

    return book
