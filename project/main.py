from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
import sqlite3
from pathlib import Path



app = FastAPI()

# ======================
# BASE PATH (important for Vercel + local)
# ======================
BASE_DIR = Path(__file__).resolve().parent

# ======================
# Database path (ONE SOURCE OF TRUTH)
# ======================
DB_PATH = BASE_DIR / "database.db"

# ======================
# Templates (cache_size=0 fixes Vercel's LRUCache bug)
# ======================
env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    auto_reload=True,
    cache_size=0
)
templates = Jinja2Templates(env=env)

# ======================
# Static files
# ======================
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# ======================
# INIT DB
# ======================
def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ======================
# HOME PAGE
# ======================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# ======================
# SUBMIT EMAIL
# ======================

@app.post("/submit-email")
def submit_email(request: Request, email: str = Form(...)):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO emails (email) VALUES (?)",
            (email,)
        )
        conn.commit()
        conn.close()
        return RedirectResponse(url="/result", status_code=303)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)
# ======================
# VIEW EMAILS (ADMIN)
# ======================
@app.get("/emails")
def get_emails():
    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute(
        "SELECT * FROM emails ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return rows