from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import os
from pydantic import BaseModel

app = FastAPI()

# Automatically finds your templates and static folders
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")

# YOUR SECRET ENDPOINTS (Browsers can never see these)
CHAT_API_URL = "https://shahid202-apichat.hf.space/chat"
TTS_API_URL = "https://shahid202-kokoro-api.hf.space/tts"

class ChatPayload(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username and password:
        return RedirectResponse(url="/dashboard", status_code=303)
    return HTMLResponse(content="Invalid Login", status_code=401)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/proxy-chat")
async def proxy_chat(payload: ChatPayload):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(CHAT_API_URL, json={"message": payload.message}, timeout=30.0)
            return response.json()
        except Exception:
            return JSONResponse(status_code=500, content={"response": "Chat Server Error"})

@app.get("/api/proxy-tts")
async def proxy_tts(text: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.get(f"{TTS_API_URL}?text={text}&voice=af_heart", timeout=30.0)
            return {"status": "success"}
        except Exception:
            return JSONResponse(status_code=500, content={"status": "error"})
          
