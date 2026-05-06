from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import sqlite3
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# HIDDEN LINKS: Stored securely in backend memory. Browsers cannot inspect this.
CHAT_API_URL = "https://shahid202-apichat.hf.space/chat"
TTS_API_URL = "https://shahid202-kokoro-api.hf.space/tts"

# Database initialization
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class ChatPayload(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/auth/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return RedirectResponse(url="/dashboard", status_code=303)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return HTMLResponse(content="<h2>Invalid Credentials. Go back and try again.</h2>", status_code=401)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# SECURE PROXY ROUTES: Your frontend calls these, hiding the real destination URLs
@app.post("/api/proxy-chat")
async def proxy_chat(payload: ChatPayload):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(CHAT_API_URL, json={"message": payload.message}, timeout=30.0)
            return response.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"response": "Chat server timeout error."})

@app.get("/api/proxy-tts")
async def proxy_tts(text: str):
    # Triggers your Hugging Face generation endpoint blindly from the server background
    async with httpx.AsyncClient() as client:
        try:
            await client.get(f"{TTS_API_URL}?text={text}&voice=af_heart", timeout=30.0)
            return {"status": "success"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"status": "error"})
