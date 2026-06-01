# 03 — FastAPI: What's Next (Skills You Haven't Done Yet)

Your 4 projects cover the core. These are the remaining production-ready skills.

---

## Skills checklist

| Skill | Status | Next.js equivalent |
|---|---|---|
| Basic routing, path/query params | ✅ Project 1 | `app/api/route.ts` |
| Pydantic validation, HTTP exceptions | ✅ Project 2 | Zod |
| SQLAlchemy ORM, dependency injection | ✅ Project 3 | Prisma/Drizzle |
| JWT auth, APIRouter, password hashing | ✅ Project 4 | next-auth |
| DB migrations (Alembic) | ❌ not yet | `prisma migrate dev` |
| Environment variables (BaseSettings) | ❌ not yet | `.env.local` |
| Testing (pytest) | ❌ not yet | Jest / Vitest |
| Background tasks | ❌ not yet | Next.js background jobs |
| CORS middleware | ❌ not yet | `next.config.js` headers |
| Async SQLAlchemy | ❌ optional | — |
| Docker | ❌ not yet | Dockerfile |

---

## 1. Alembic — database migrations

Right now your projects use:
```python
models.Base.metadata.create_all(bind=engine)
```

This creates tables on startup but **can't modify existing tables** — adding a column requires dropping and recreating everything. That's fine for learning, not for production.

**Alembic** = `prisma migrate dev` for SQLAlchemy.

```bash
pip install alembic
alembic init alembic          # creates alembic/ folder + alembic.ini

# generate a migration after changing models.py
alembic revision --autogenerate -m "add owner_id to todos"

# apply it
alembic upgrade head

# rollback
alembic downgrade -1
```

Alembic reads your SQLAlchemy models, diffs them against the current DB, and generates SQL migration scripts. You version-control the migration files just like Prisma's `migrations/` folder.

---

## 2. Environment variables with Pydantic BaseSettings

Right now secrets are hardcoded:
```python
# auth.py — don't do this in production
SECRET_KEY = "fdc879ec395cec6ca4b0c7fa9f37694fb3fef3eb1b271b9edcdf28a988dc5511"
```

**The fix — Pydantic BaseSettings:**

```bash
pip install pydantic-settings
```

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"

settings = Settings()
```

```env
# .env
SECRET_KEY=fdc879ec395cec6ca4b0c7fa9f37694fb3fef3eb1b271b9edcdf28a988dc5511
DATABASE_URL=postgresql://user:pass@localhost/mydb
```

```python
# use it anywhere
from config import settings

jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
```

This is the FastAPI equivalent of `process.env.SECRET_KEY` in Next.js, but with type validation.

---

## 3. pytest — testing

FastAPI has a built-in `TestClient` that wraps your app for testing without running a server.

```bash
pip install pytest httpx
```

```python
# test_todos.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_all_todos():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_todo():
    response = client.post("/todo", json={
        "title": "Test todo",
        "description": "Testing",
        "priority": 3,
        "complete": False,
    })
    assert response.status_code == 201
```

```bash
pytest                    # run all tests
pytest test_todos.py -v   # verbose
pytest -k "test_create"   # run matching tests
```

`TestClient` = like `supertest` in Node.js. No server needed, tests run in-process.

For authenticated routes, you'll override the dependency in tests:
```python
def override_get_current_user():
    return {"username": "testuser", "id": 1}

app.dependency_overrides[get_current_user] = override_get_current_user
```

This replaces the JWT dependency with a mock — like mocking middleware in Jest.

---

## 4. Background tasks

For operations you don't want to block the HTTP response (sending emails, logging, cleanup):

```python
from fastapi import BackgroundTasks

def send_welcome_email(email: str):
    # runs after the response is sent
    print(f"Sending email to {email}")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest,
    background_tasks: BackgroundTasks,       # injected automatically
):
    # create user...
    background_tasks.add_task(send_welcome_email, create_user_request.email)
    # response returns immediately, email sends in background
```

For heavy background work (queues, retries), use **Celery** with Redis — but `BackgroundTasks` covers most simple cases.

---

## 5. CORS middleware

When your Next.js frontend calls your FastAPI backend from a different origin:

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Same concept as `Access-Control-Allow-Origin` headers in `next.config.js`.

---

## 6. Response models — shape what you return

Right now your routes return raw SQLAlchemy models. In production, you want to control exactly what fields the API exposes (never return `hashed_password`):

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    # no hashed_password field — it won't appear in responses

    model_config = {"from_attributes": True}  # lets Pydantic read SQLAlchemy models

@router.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int, db: db_dependency):
    return db.query(Users).filter(Users.id == id).first()
    # FastAPI filters the output through UserResponse automatically
```

`response_model=` = like a TypeScript return type that's also enforced at runtime.

---

## 7. Prefix and tags for all routers

When you have many routers, add prefix and tags to keep Swagger docs clean:

```python
# routers/todos.py
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

# routers/users.py
router = APIRouter(
    prefix="/users",
    tags=["users"],
)
```

All routes in `todos.py` become `/todos/...`, all in `users.py` become `/users/...`.
Swagger UI at `/docs` groups them by tag — much easier to navigate.

---

## 8. Docker — packaging for deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t my-fastapi-app .
docker run -p 8000:8000 my-fastapi-app
```

Same pattern as any Node.js Dockerfile — copy deps, install, copy code, run.

---

## Recommended learning order from here

1. **BaseSettings + .env** — do this immediately, remove hardcoded secrets
2. **CORS** — you'll need it the moment you connect a frontend
3. **Response models** — good security habit
4. **pytest** — start writing tests for your auth routes
5. **Alembic** — when you start changing your schema
6. **Background tasks** — when you need async side effects
7. **Docker** — when you deploy

---

## Full production stack reference

```
FastAPI         → framework (like Express/Next.js API)
Pydantic        → validation (like Zod)
SQLAlchemy      → ORM (like Prisma/Drizzle)
Alembic         → migrations (like prisma migrate)
python-jose     → JWT (like jose in Node)
passlib+bcrypt  → password hashing (like bcrypt in Node)
uvicorn         → ASGI server (like Node.js runtime)
pydantic-settings → env config (like dotenv)
pytest+httpx    → testing (like Jest+supertest)
Docker          → deployment packaging
```
