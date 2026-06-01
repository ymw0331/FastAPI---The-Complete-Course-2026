# 00 — Python Environment & Syntax Basics

Coming from Next.js, the tooling feels different but the concepts map 1:1.

---

## Python vs Node: the tooling comparison

| Concept | Node / Next.js | Python |
|---|---|---|
| Runtime | `node` | `python` or `python3` |
| Package manager | `npm` / `pnpm` | `pip` |
| Package registry | npmjs.com | pypi.org |
| Dependency file | `package.json` | `requirements.txt` |
| Lock file | `package-lock.json` | (no lock by default, use `pip freeze`) |
| Local packages | `node_modules/` | `.venv/` |
| Run dev server | `npm run dev` | `uvicorn main:app --reload` |
| Script runner | `package.json` scripts | just run `python filename.py` |

---

## What is `.venv`?

In Node, when you run `npm install`, packages go into `node_modules/` inside your project.
Python's equivalent is a **virtual environment** — a folder (usually named `.venv`) that contains:
- its own Python interpreter copy
- all packages installed with `pip` for that project only

Without `.venv`, every `pip install` goes into your **global Python** — shared across all projects on your machine. That causes version conflicts fast.

```
# your machine without .venv:
Project A needs fastapi==0.100
Project B needs fastapi==0.80
# → they can't coexist globally
```

With `.venv`, each project is isolated — exactly like `node_modules/`.

---

## Global Python vs Project Python

| | Global Python | Project `.venv` |
|---|---|---|
| Location | `/usr/bin/python3` or `/opt/homebrew/bin/python3` | `yourproject/.venv/bin/python` |
| Packages | shared by everything | isolated to this project |
| Risk | version conflicts between projects | none |
| When to use | system scripts, one-off tools | always for projects |

---

## Setting up a new Python project (your workflow)

```bash
# 1. create a project folder
mkdir my-project && cd my-project

# 2. create a virtual environment inside it
python3 -m venv .venv

# 3. activate it (Mac/Linux)
source .venv/bin/activate

# 4. your prompt changes:
# (.venv) yourname@machine my-project %

# 5. now pip installs go into .venv only
pip install fastapi uvicorn sqlalchemy

# 6. save your dependencies (like package.json)
pip freeze > requirements.txt

# 7. deactivate when done
deactivate
```

When someone else clones your project:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # like npm install
```

---

## VSCode / Cursor setup

1. Open the project folder
2. `Cmd+Shift+P` → **Python: Select Interpreter**
3. Pick the one that says `.venv` — e.g. `Python 3.12.x ('.venv': venv)`
4. If it's not listed, click **Enter interpreter path** and browse to `.venv/bin/python`

The interpreter shown in the bottom-right status bar should say `('.venv')`.

For the terminal inside VSCode, it auto-activates `.venv` once you've selected the interpreter.
If not: `source .venv/bin/activate` manually.

> Your existing projects already have `.venv` set up. In Project 4, it's at `Project 4/TodoApp/.venv/`.

---

## Python version

Check what you have:
```bash
python3 --version
```

FastAPI requires Python 3.10+. Python 3.12 is recommended in 2026.

If you need to manage multiple Python versions, use **pyenv** (the Python equivalent of `nvm`):
```bash
brew install pyenv
pyenv install 3.12
pyenv local 3.12   # sets .python-version file in this folder
```

---

## requirements.txt — your package.json equivalent

```txt
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.0
pydantic==2.7.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.3
```

Install all: `pip install -r requirements.txt`
Add a package: `pip install newpackage` then `pip freeze > requirements.txt`

---

## Running your FastAPI app

```bash
# from inside the project folder, with .venv activated:
uvicorn main:app --reload

# main      = the filename (main.py)
# app       = the FastAPI() instance variable name
# --reload  = like Next.js hot reload
```

Then open: http://127.0.0.1:8000
Interactive API docs: http://127.0.0.1:8000/docs  ← this is Swagger UI, free with FastAPI

---

## .gitignore

Always ignore `.venv` and compiled cache:
```
.venv/
__pycache__/
*.pyc
*.db
.env
```

This is already in your projects. `__pycache__/` = Python's compiled bytecode cache, like Next.js's `.next/` build output.
