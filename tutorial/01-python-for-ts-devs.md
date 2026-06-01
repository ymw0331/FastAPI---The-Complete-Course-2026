# 01 — Python for TypeScript Developers

Every concept you know in TypeScript has a Python equivalent. This is a direct mapping.

---

## Variables

```typescript
// TypeScript
const name = "Wayne"
let age = 30
const isActive: boolean = true
```

```python
# Python — no const/let, just assign
name = "Wayne"
age = 30
is_active = True   # note: True/False capitalized, snake_case naming
```

Python uses `snake_case` everywhere. TypeScript uses `camelCase`. That's the biggest style shift.

No `const` — Python doesn't enforce immutability at the variable level.

---

## Type hints (like TypeScript types)

Python is dynamically typed by default, but you can add type hints — and FastAPI/Pydantic require them.

```typescript
// TypeScript
function greet(name: string, age: number): string {
  return `Hello ${name}, you are ${age}`
}
```

```python
# Python
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"   # f-string = template literal
```

Type hints are not enforced at runtime (unlike TypeScript's compile-time checks), but FastAPI uses them to auto-validate and auto-document your API.

---

## Common type mappings

| TypeScript | Python |
|---|---|
| `string` | `str` |
| `number` | `int` or `float` |
| `boolean` | `bool` |
| `null` / `undefined` | `None` |
| `string \| null` | `Optional[str]` or `str \| None` (Python 3.10+) |
| `string[]` | `list[str]` |
| `Record<string, any>` | `dict[str, any]` |
| `any` | `Any` (from `typing`) |

```python
from typing import Optional

def find_user(user_id: int) -> Optional[dict]:
    # returns a dict or None
    ...
```

---

## Functions

```typescript
// TypeScript
function add(a: number, b: number): number {
  return a + b
}

// arrow function
const double = (x: number) => x * 2
```

```python
# Python
def add(a: int, b: int) -> int:
    return a + b

# lambda (like arrow function, but limited to one expression)
double = lambda x: x * 2
```

**Indentation matters** — Python uses indentation (4 spaces) instead of `{}` braces.

---

## If / else

```typescript
if (score > 90) {
  console.log("A")
} else if (score > 70) {
  console.log("B")
} else {
  console.log("C")
}
```

```python
if score > 90:
    print("A")
elif score > 70:     # note: elif not else if
    print("B")
else:
    print("C")
```

---

## None checks (like TypeScript's optional chaining)

```typescript
// TypeScript
if (user?.name) { ... }
const name = user?.name ?? "Guest"
```

```python
# Python
if user is not None:
    print(user.name)

name = user.name if user is not None else "Guest"

# or use: if user:  (falsy check, same as JS)
```

No `?.` in Python. You explicitly check `is not None`.

---

## Lists (arrays)

```typescript
const fruits: string[] = ["apple", "banana"]
fruits.push("cherry")
fruits.map(f => f.toUpperCase())
fruits.filter(f => f.startsWith("a"))
```

```python
fruits: list[str] = ["apple", "banana"]
fruits.append("cherry")                         # .push() → .append()
[f.upper() for f in fruits]                     # .map() → list comprehension
[f for f in fruits if f.startswith("a")]        # .filter() → list comprehension
```

**List comprehension** is Python's killer feature — replaces `.map()` and `.filter()`:
```python
# [expression for item in list if condition]
doubled = [x * 2 for x in [1, 2, 3]]           # [2, 4, 6]
evens   = [x for x in range(10) if x % 2 == 0] # [0, 2, 4, 6, 8]
```

---

## Dicts (objects / Records)

```typescript
const user: Record<string, any> = { name: "Wayne", age: 30 }
user["email"] = "wayne@example.com"
const name = user.name
const missing = user.role ?? "guest"
```

```python
user: dict = {"name": "Wayne", "age": 30}
user["email"] = "wayne@example.com"
name = user["name"]            # or user.get("name")
missing = user.get("role", "guest")   # .get() with default = ?? nullish coalescing
```

`.get("key", default)` is the Python equivalent of `obj.key ?? default`.

---

## Classes

```typescript
// TypeScript
interface User {
  id: number
  name: string
}

class UserService {
  private users: User[] = []

  addUser(user: User): void {
    this.users.push(user)
  }
}
```

```python
# Python
class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class UserService:
    def __init__(self):
        self.users: list[User] = []

    def add_user(self, user: User) -> None:
        self.users.append(user)
        # note: self is explicit — like 'this' but you must always pass it
```

`self` = `this`. Every method must take `self` as the first parameter.

---

## Async / Await

This is the same concept, near-identical syntax:

```typescript
// TypeScript
async function fetchUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`)
  return res.json()
}
```

```python
# Python
import httpx

async def fetch_user(id: int) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"/api/users/{id}")
        return res.json()
```

In FastAPI, you mark route handlers as `async def` when you want non-blocking I/O.
Regular `def` also works — FastAPI runs it in a thread pool automatically.

---

## Decorators (like @ in TypeScript/Angular)

```python
# A decorator wraps a function — like a higher-order function
@app.get("/books")
async def read_books():
    return books
```

`@app.get("/books")` is equivalent to:
```python
read_books = app.get("/books")(read_books)
```

You've already used decorators in all your projects. They're FastAPI's core API.

---

## Imports / Modules

```typescript
// TypeScript
import { useState } from "react"
import type { User } from "./types"
import * as fs from "fs"
```

```python
# Python
from fastapi import FastAPI, Depends    # named imports
from typing import Optional             # type imports (no separate 'import type')
import os                               # whole module import

from models import Todos                # relative-style import from same project
from .auth import get_current_user      # explicit relative import (the dot means "same package")
```

The `.` prefix (like `from .auth import`) means "from the same folder/package". You've already used this in `routers/todos.py`.

---

## Error handling

```typescript
try {
  const data = JSON.parse(input)
} catch (error) {
  console.error(error)
}
```

```python
try:
    data = json.loads(input)
except ValueError as error:
    print(error)
except Exception as error:   # catch-all, like catch(error)
    print(error)
finally:
    print("always runs")
```

In FastAPI you usually raise `HTTPException` instead of generic exceptions:
```python
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Not found")
```

---

## String formatting

```typescript
const msg = `Hello ${name}, you have ${count} items`
```

```python
msg = f"Hello {name}, you have {count} items"   # f-string, same idea
```

---

## Quick reference cheat sheet

| TypeScript | Python |
|---|---|
| `console.log()` | `print()` |
| `===` | `==` |
| `!==` | `!=` |
| `&&` | `and` |
| `\|\|` | `or` |
| `!` | `not` |
| `null` / `undefined` | `None` |
| `true` / `false` | `True` / `False` |
| `for (const x of arr)` | `for x in arr:` |
| `arr.length` | `len(arr)` |
| `typeof x === "string"` | `isinstance(x, str)` |
| `Object.keys(obj)` | `obj.keys()` |
| `{...obj, key: val}` | `{**obj, "key": val}` |
| `[...arr1, ...arr2]` | `[*arr1, *arr2]` |
