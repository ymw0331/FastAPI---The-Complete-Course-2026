# 02 — FastAPI Mental Model (mapped to your actual projects)

This walks through every pattern in your 4 projects and maps them to Next.js equivalents.

---

## The big picture

| Next.js | FastAPI |
|---|---|
| `app/api/route.ts` | `main.py` + routers |
| `export async function GET()` | `@app.get("/path")` |
| `NextRequest` / `NextResponse` | handled automatically |
| Zod schema | Pydantic `BaseModel` |
| `middleware.ts` | `Depends()` dependency injection |
| Prisma / Drizzle | SQLAlchemy |
| `prisma migrate dev` | Alembic (covered in file 03) |
| `next dev` | `uvicorn main:app --reload` |
| `.env.local` | `.env` + Pydantic `BaseSettings` |
| JWT via `next-auth` or `jose` | `python-jose` + `passlib` |

---

## Project 1 — Basic routing (books.py)

### `@app.get()` = Next.js route handler

```python
# FastAPI
@app.get("/books")
async def read_all_books():
    return BOOKS
```

```typescript
// Next.js equivalent
export async function GET() {
  return Response.json(BOOKS)
}
```

FastAPI auto-serializes whatever you return — lists, dicts, Pydantic models, all become JSON automatically.

### Path parameters

```python
@app.get("/books/{book_title}")
async def read_book(book_title: str):
    ...
```

```typescript
// Next.js: app/books/[book_title]/route.ts
export async function GET(req, { params }) {
  const { book_title } = params
}
```

The `{book_title}` in the path and `book_title: str` in the function signature are linked by name — FastAPI wires them automatically.

### Query parameters

```python
@app.get("/books/")
async def read_by_category(category: str):   # not in path = query param
    ...
```

```typescript
// Next.js
const category = req.nextUrl.searchParams.get("category")
```

In FastAPI: if a function parameter is **not** in the path, it's automatically a query param. No extra config needed.

---

## Project 2 — Pydantic models (books2.py)

### Pydantic `BaseModel` = Zod schema

```python
# FastAPI
class BookRequest(BaseModel):
    title: str = Field(min_length=3)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)
```

```typescript
// Zod equivalent
const BookRequest = z.object({
  title: z.string().min(3),
  rating: z.number().int().gt(0).lt(6),
  publishedDate: z.number().int().gt(1999).lt(2031),
})
```

Pydantic validates the request body automatically. If validation fails, FastAPI returns a `422 Unprocessable Entity` with detailed error messages — you get this for free, no manual validation code.

### Using the model in a route

```python
@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):   # FastAPI parses + validates body here
    new_book = Book(**book_request.model_dump())    # model_dump() = like toJSON() / spread
    ...
```

`**book_request.model_dump()` unpacks the Pydantic model into keyword arguments — equivalent to `{...bookRequest}` spread in JavaScript.

### HTTP status codes

```python
from starlette import status

@app.get("/books", status_code=status.HTTP_200_OK)
@app.post("/books", status_code=status.HTTP_201_CREATED)
@app.put("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
```

Use `status.HTTP_xxx` constants instead of raw numbers — more readable, same as using named constants in any language.

### HTTPException = throwing errors

```python
raise HTTPException(status_code=404, detail="Item not found")
```

```typescript
// Next.js
return Response.json({ error: "Not found" }, { status: 404 })
// or with next-safe-action:
throw new Error("Not found")
```

FastAPI catches `HTTPException` and turns it into a proper JSON error response automatically.

---

## Project 3 — SQLAlchemy + Dependency Injection (main.py)

### SQLAlchemy = Prisma / Drizzle ORM

```python
# models.py — define your table
class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    complete = Column(Boolean, default=False)
```

```typescript
// Prisma equivalent in schema.prisma
model Todo {
  id       Int     @id @default(autoincrement())
  title    String
  complete Boolean @default(false)
}
```

### database.py — the connection setup

```python
engine = create_engine("sqlite:///./todos.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

```typescript
// Prisma equivalent
const prisma = new PrismaClient()
```

`engine` = the connection pool. `SessionLocal` = a factory that creates a DB session per request. `Base` = the base class all your models extend.

### Dependency Injection with `Depends()` = middleware / React context

```python
def get_db():
    db = SessionLocal()
    try:
        yield db        # like a context manager — gives the session, then cleans up after
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db: db_dependency):   # FastAPI calls get_db() and injects the result
    return db.query(Todos).all()
```

`Depends(get_db)` means "before calling this route, run `get_db()` and pass the result as `db`". It's FastAPI's dependency injection system — like React context but for function arguments, or like NestJS providers.

`yield` in `get_db()` means: give the `db` to the route, run the route, then run `db.close()` after. It's a generator used as a context manager.

### SQLAlchemy query syntax

```python
# SELECT * FROM todos
db.query(Todos).all()

# SELECT * FROM todos WHERE id = ?
db.query(Todos).filter(Todos.id == todo_id).first()

# INSERT
todo = Todos(title="Buy milk", priority=1, complete=False)
db.add(todo)
db.commit()

# DELETE
db.query(Todos).filter(Todos.id == todo_id).delete()
db.commit()
```

```typescript
// Prisma equivalents
prisma.todo.findMany()
prisma.todo.findFirst({ where: { id: todoId } })
prisma.todo.create({ data: { title: "Buy milk", priority: 1 } })
prisma.todo.delete({ where: { id: todoId } })
```

---

## Project 4 — JWT Auth + Routers (auth.py, todos.py)

### `APIRouter` = Next.js route groups

```python
# routers/auth.py
router = APIRouter(
    prefix="/auth",   # all routes in this file start with /auth
    tags=["auth"],    # groups them in Swagger docs
)

# routers/todos.py
router = APIRouter()

# main.py — register routers (like importing route groups)
app.include_router(auth.router)
app.include_router(todos.router)
```

```typescript
// Next.js equivalent: just folder structure
// app/auth/route.ts    → /auth
// app/todos/route.ts   → /todos
```

### Password hashing

```python
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = bcrypt_context.hash("mypassword")          # hash on register
valid  = bcrypt_context.verify("mypassword", hashed) # verify on login
```

Same as `bcrypt` in Node.js — `bcrypt.hash()` and `bcrypt.compare()`.

### JWT — create and decode

```python
from jose import jwt

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"

# create token (on login)
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    payload = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# decode token (on each request)
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
username = payload.get("sub")
```

`sub` = "subject" — JWT standard claim for the user identifier. Same convention as `next-auth`.

### OAuth2 bearer token flow

```python
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return {"username": payload.get("sub"), "id": payload.get("id")}
```

`OAuth2PasswordBearer` extracts the Bearer token from the `Authorization` header automatically. `get_current_user` is itself a dependency — it can be injected into routes:

```python
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    # user is already validated and decoded here
    return db.query(Todos).filter(Todos.owner_id == user["id"]).all()
```

This is the FastAPI pattern for protected routes — no middleware file, just a dependency.

---

## How the 4 projects connect (progression)

```
Project 1: raw dicts → basic routing, path/query params
     ↓
Project 2: Pydantic models → type-safe request bodies, validation, HTTP exceptions
     ↓
Project 3: SQLAlchemy → real database, dependency injection, session management
     ↓
Project 4: JWT + routers → auth, protected endpoints, code organization
```

Each project adds exactly one layer. By Project 4 you have a production-shaped architecture.
