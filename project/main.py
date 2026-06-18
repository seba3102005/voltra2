from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import psycopg2
import os

app = FastAPI()

# ======================
# BASE PATH
# ======================
BASE_DIR = Path(__file__).resolve().parent

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
# DB CONNECTION
# ======================
def get_conn():
    return psycopg2.connect(os.environ["POSTGRES_URL"])

# ======================
# INIT DB
# ======================
def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

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
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
        conn.commit()
        cur.close()
        conn.close()
        return RedirectResponse(url="/result", status_code=303)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

# ======================
# RESULT PAGE (404 STYLE)
# ======================
@app.get("/result", response_class=HTMLResponse)
def result(request: Request):
    return templates.TemplateResponse(request=request, name="404.html")

# ======================
# VIEW EMAILS (ADMIN)
# ======================
@app.get("/emails")
def get_emails():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM emails ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)