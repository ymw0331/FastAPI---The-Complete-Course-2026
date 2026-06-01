# 04 — Pydantic v2 Changes & Python Import System

Two things that will trip you up the moment you read newer docs or reorganise your project.

---

## Part 1: Pydantic v2

FastAPI now uses Pydantic v2 by default. The API changed in a few key ways.
Your existing code works but uses deprecated v1 patterns — you'll see warnings and newer examples won't match.

---

### `.dict()` → `.model_dump()`

```python
# v1 (deprecated — your current code uses this)
todo_model = Todos(**todo_request.dict())

# v2 (correct)
todo_model = Todos(**todo_request.model_dump())
```

Your `Project 3` and `Project 4` both use `.dict()`. It still works but will be removed in a future version.

---

### `.json()` → `.model_json()`

```python
# v1
user.json()

# v2
user.model_json()
```

---

### `schema()` → `model_json_schema()`

```python
# v1
BookRequest.schema()

# v2
BookRequest.model_json_schema()
```

---

### `orm_mode = True` → `from_attributes = True`

This one comes up when you use `response_model=` with SQLAlchemy objects (covered in `03-fastapi-whats-next.md`):

```python
# v1 (deprecated)
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# v2 (correct)
class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}
```

Your `Project 2` already uses the v2 style for `json_schema_extra`:
```python
model_config = {
    "json_schema_extra": { "example": { ... } }
}
```
That's correct v2 syntax. Just extend it with `"from_attributes": True` when needed.

---

### `validator` → `field_validator`

Custom field validation changed:

```python
# v1 (deprecated)
from pydantic import validator

class BookRequest(BaseModel):
    title: str

    @validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v

# v2 (correct)
from pydantic import field_validator

class BookRequest(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v
```

Two changes: decorator renamed to `@field_validator`, and you must add `@classmethod`.

---

### `root_validator` → `model_validator`

For validation that spans multiple fields:

```python
# v1 (deprecated)
from pydantic import root_validator

@root_validator
def check_dates(cls, values):
    ...

# v2 (correct)
from pydantic import model_validator

@model_validator(mode="after")
def check_dates(self):
    # self is the model instance, access fields directly
    if self.start_date > self.end_date:
        raise ValueError("start must be before end")
    return self
```

---

### `Optional[str]` — still works, but Python 3.10+ has cleaner syntax

```python
# both are valid in v2
from typing import Optional
name: Optional[str] = None   # old style, still works

name: str | None = None      # Python 3.10+ style, preferred in newer code
```

You'll see both in docs and examples. They're identical at runtime.

---

### Quick v1 → v2 migration cheat sheet

| v1 (deprecated) | v2 (current) |
|---|---|
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_json()` |
| `.schema()` | `.model_json_schema()` |
| `class Config: orm_mode = True` | `model_config = {"from_attributes": True}` |
| `@validator("field")` | `@field_validator("field")` + `@classmethod` |
| `@root_validator` | `@model_validator(mode="after")` |
| `parse_obj(data)` | `model_validate(data)` |
| `parse_raw(json_str)` | `model_validate_json(json_str)` |

---

---

## Part 2: Python Import System

This is the #1 thing that breaks when you reorganise a project.

---

### How Python finds modules

When you write `import something`, Python looks in:
1. The current directory
2. Directories in `PYTHONPATH`
3. Standard library
4. Installed packages in `.venv`

This is why running `python main.py` from the project root works, but running it from a subdirectory breaks imports.

---

### Absolute vs relative imports

```python
# absolute import — full path from the project root
from routers.auth import get_current_user
from models import Todos
from database import SessionLocal

# relative import — relative to the current file's location
from .auth import get_current_user    # . = same folder (routers/)
from ..models import Todos            # .. = one folder up
```

In your `Project 4/TodoApp/routers/todos.py`:
```python
from .auth import get_current_user   # works because todos.py and auth.py are in the same routers/ folder
```

The `.` means "look in the same package (folder) I'm in." Without the dot:
```python
from auth import get_current_user    # would fail — Python looks for a top-level 'auth' module
```

---

### What makes a folder a "package"

A folder becomes a Python package (importable) when it contains an `__init__.py` file.

```
TodoApp/
├── main.py
├── models.py
├── database.py
└── routers/
    ├── __init__.py    ← this makes routers/ a package
    ├── auth.py
    └── todos.py
```

Without `__init__.py`, Python treats `routers/` as just a folder, not a module, and `from routers.auth import ...` would fail.

`__init__.py` can be empty — its presence is what matters. It can also run code when the package is imported (rarely needed).

Check your Project 4 — it should have `routers/__init__.py`. If it doesn't, the relative imports work because of how `uvicorn` sets up the path.

---

### Why moving files breaks imports

Say you have:
```
TodoApp/
├── main.py
└── routers/
    └── auth.py        ← contains: from models import Users
```

If you move `auth.py` into a subdirectory:
```
TodoApp/
├── main.py
└── routers/
    └── v1/
        └── auth.py    ← now 'from models import Users' breaks
```

Because `models.py` is in `TodoApp/`, not `TodoApp/routers/v1/`. Fix it with an absolute import:
```python
from models import Users    # still works if you run uvicorn from TodoApp/
```

Or a relative import going up two levels:
```python
from ...models import Users  # ../../models.py from routers/v1/auth.py
```

**Rule of thumb:** always run your server (`uvicorn main:app`) from the project root. Python adds that directory to the path, making all absolute imports work from there.

---

### `__pycache__` explained

```
routers/
├── __pycache__/
│   ├── auth.cpython-312.pyc
│   └── todos.cpython-312.pyc
├── auth.py
└── todos.py
```

`__pycache__/` = Python's compiled bytecode cache. Like Next.js's `.next/` folder.

- Python compiles `.py` → `.pyc` on first run for faster subsequent imports
- You never edit these files
- Always in `.gitignore`
- Safe to delete — Python recreates them on next run
- `cpython-312` = compiled with CPython 3.12 (the standard Python runtime)

---

### Common import errors and fixes

**`ModuleNotFoundError: No module named 'models'`**
→ You're running python from the wrong directory. `cd` to the folder containing `main.py` first.

**`ImportError: attempted relative import with no known parent package`**
→ You're running a file directly (`python routers/auth.py`) instead of through the app (`uvicorn main:app`). Relative imports only work when Python knows the package structure.

**`ImportError: cannot import name 'X' from 'Y'`**
→ The name doesn't exist in that module, or there's a circular import (A imports B, B imports A). Fix circular imports by moving shared code to a third module that both import from.

---

### The import pattern in your projects

```python
# main.py (project root) — uses absolute imports
import models
from database import engine
from routers import auth, todos

# routers/todos.py — uses relative import for sibling file
from .auth import get_current_user   # auth.py is in the same routers/ folder

# routers/auth.py — uses absolute imports for root-level modules
from models import Users
from database import SessionLocal
```

This pattern (absolute from root, relative for siblings) is the standard FastAPI convention. Stick to it and you won't have import issues.
