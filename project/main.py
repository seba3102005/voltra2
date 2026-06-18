from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from pathlib import Path

app = FastAPI()


BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)
templates = Jinja2Templates(directory="templates")


def init_db():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "database.db")

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


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/submit-email")
def submit_email(email: str = Form(...)):
    conn = sqlite3.connect("database.db")

    conn.execute(
        "INSERT INTO emails (email) VALUES (?)",
        (email,)
    )

    conn.commit()
    conn.close()

    return RedirectResponse(
        url="/result",
        status_code=303
    )


@app.get("/result", response_class=HTMLResponse)
def not_found(request: Request):
    return templates.TemplateResponse(
        "404.html",
        {"request": request}
    )


@app.get("/emails")
def get_emails():
    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        "SELECT * FROM emails ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return rows