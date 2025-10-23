import os
from typing import Optional
from contextlib import asynccontextmanager
#from AI.app import generate_educational_video

from fastapi import FastAPI, Request, Form, Depends, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, create_engine, select
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer, BadSignature 
from sqlalchemy import func 

from pathlib import Path
from dotenv import load_dotenv

templates = Jinja2Templates(directory="MAIN/templates")

# === Load .env dari lokasi AI, MAIN, atau root ===
BASE_DIR = Path(__file__).resolve().parent
project_root = BASE_DIR.parent
env_paths = [
    BASE_DIR / ".env",           # MAIN/.env
    project_root / ".env",       # FP/.env
    project_root / "AI" / ".env" # FP/AI/.env
]
for env in env_paths:
    if env.exists():
        load_dotenv(dotenv_path=env)
        print(f"✅ Loaded .env from: {env}")
        break
else:
    print("⚠️ No .env file found in MAIN, FP, or AI.")

# === Database URL ===
uri_db = os.getenv("DATABASE_URL")
if not uri_db:
    raise RuntimeError("❌ DATABASE_URL not found in environment variables")

from sqlmodel import SQLModel, Field, Session, create_engine, select
engine = create_engine(uri_db, echo=False)

# ---------------- Models DB----------------
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str

class ChatFolder(SQLModel, table=True):
    __tablename__ = "chatfolders"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_folder_id: int = Field(foreign_key="chatfolders.id")
    role: bool  # True=user, False=ai
    content: str
    video_url: Optional[str] = None  # ✅ kolom baru
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    id: Optional[int] = Field(default=None, primary_key=True)
    nama: str
    nrp: str
    kelompok: str
    rating: int
    review: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ---------------- App ----------------
app = FastAPI()
templates = Jinja2Templates(directory="MAIN/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app.router.lifespan_context = lifespan

# ---------------- Session (secure cookie) ----------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")  # >>> changed
signer = URLSafeSerializer(SECRET_KEY, salt="session")      # >>> changed

def set_session(response: Response, user_id: int, username: str):  # >>> changed
    token = signer.dumps({"id": user_id, "username": username})
    response.set_cookie(
        key="session",
        value=token, 
        httponly=True,
        samesite="lax",
        secure=False,  # set True di production (HTTPS)
        max_age=60*60*24*7,  # 7 hari
        path="/",
    )

def clear_session(response: Response):  # >>> changed
    response.delete_cookie("session", path="/")

def get_session_data(request: Request):  # >>> changed
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        return signer.loads(token)  # {"id":..., "username":...}
    except BadSignature:
        return None

def current_user_required(request: Request):  # >>> changed
    data = get_session_data(request)
    if not data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == data["id"])).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")
        return user

# ---------------- Pages ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": None})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})

@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=303)   # >>> changed
    clear_session(resp)
    return resp

@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request, user: User = Depends(current_user_required)):  # >>> changed
    with Session(engine) as session:
        chat_list = session.exec(
            select(ChatFolder)
            .where(ChatFolder.user_id == user.id)
            .order_by(ChatFolder.id.desc())
        ).all()
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "username": user.username, "chats": chat_list}
    )
    
@app.get("/reviews", response_class=HTMLResponse)
def reviews_page(request: Request, user: User = Depends(current_user_required)):
    """Tampilkan halaman review"""
    with Session(engine) as session:
        all_reviews = session.exec(
            select(Review).order_by(Review.created_at.desc())
        ).all()
    return templates.TemplateResponse(
        "reviews.html",
        {"request": request, "username": user.username, "reviews": all_reviews}
    )


@app.post("/api/reviews")
def submit_review(data: dict, user: User = Depends(current_user_required)):
    """Terima review dari form frontend (AJAX POST)"""
    try:
        nama = data.get("nama", "").strip()
        nrp = data.get("nrp", "").strip()
        kelompok = data.get("kelompok", "").strip()
        rating = int(data.get("rating", 0))
        review_text = data.get("review", "").strip()

        if not nama or not nrp or not kelompok or not review_text or rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Invalid input")

        with Session(engine) as session:
            new_review = Review(
                nama=nama,
                nrp=nrp,
                kelompok=kelompok,
                rating=rating,
                review=review_text
            )
            session.add(new_review)
            session.commit()
            session.refresh(new_review)

            return {
                "ok": True,
                "review": {
                    "nama": new_review.nama,
                    "nrp": new_review.nrp,
                    "kelompok": new_review.kelompok,
                    "rating": new_review.rating,
                    "review": new_review.review,
                    "created_at": new_review.created_at.isoformat()
                }
            }

    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="Gagal menyimpan review")
    
@app.get("/api/reviews")
def get_all_reviews():
    """Ambil semua review untuk tabel frontend"""
    with Session(engine) as session:
        reviews = session.exec(select(Review).order_by(Review.created_at.desc())).all()
    return [
        {
            "nama": r.nama,
            "nrp": r.nrp,
            "kelompok": r.kelompok,
            "rating": r.rating,
            "review": r.review,
            "created_at": r.created_at.isoformat()
        }
        for r in reviews
    ]

# ---------------- Auth Actions ----------------
@app.post("/register", response_class=HTMLResponse)
def register_action(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    if len(password.encode("utf-8")) > 72:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Password terlalu panjang (maks 72 byte)."},
            status_code=400
        )
    if len(username) < 3:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Username minimal 3 karakter."}, status_code=400)
    if "@" not in email:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Email tidak valid."}, status_code=400)
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Password minimal 6 karakter."}, status_code=400)

    with Session(engine) as session:
        exists = session.exec(select(User).where((User.username == username) | (User.email == email))).first()
        if exists:
            return templates.TemplateResponse("register.html", {"request": request, "message": "Username atau email sudah terdaftar."}, status_code=400)

        user = User(username=username, email=email, password_hash=pwd_ctx.hash(password))
        session.add(user)
        session.commit()
        session.refresh(user)

    # >>> set cookie & langsung menuju /chat (tanpa query)
    resp = RedirectResponse(url="/chat", status_code=303)
    set_session(resp, user.id, user.username)
    return resp

@app.post("/login", response_class=HTMLResponse)
def login_action(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...),
):
    # Cek apakah username/email ada
    with Session(engine) as session:
        q = select(User).where((User.username == username_or_email) | (User.email == username_or_email))
        user = session.exec(q).first()

    # Username/email tidak ditemukan
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Akun tidak ditemukan. Periksa username atau email Anda."},
            status_code=400
        )

    # Password salah
    if not pwd_ctx.verify(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Password salah. Coba lagi."},
            status_code=400
        )

    # Kalau semua benar → set session & redirect
    resp = RedirectResponse(url="/chat", status_code=303)
    set_session(resp, user.id, user.username)
    return resp

# ---------------- Chats & Messages API (protected) ----------------
class NewChatIn(BaseModel):
    title: str | None = None

class PostMessageIn(BaseModel):
    content: str

# cek apakah akun ada (username ATAU email) 
@app.get("/api/check-account")
def api_check_account(q: str):
    """
    q bisa berupa username ATAU email.
    Return: {"exists": True/False}
    """
    with Session(engine) as session:
        user = session.exec(
            select(User).where((User.username == q) | (User.email == q))
        ).first()
    return {"exists": bool(user)}

@app.post("/api/chats")
def api_create_chat(payload: NewChatIn, user: User = Depends(current_user_required)):  # >>> changed
    with Session(engine) as session:
        title = (payload.title or "New chat").strip() or "New chat"
        chat = ChatFolder(user_id=user.id, title=title)
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return {"id": chat.id, "title": chat.title}



@app.get("/api/chats/{chat_id}/messages")
def api_get_messages(chat_id: int, user: User = Depends(current_user_required)):  # >>> changed
    with Session(engine) as session:
        chat = session.get(ChatFolder, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(status_code=404, detail="Not found")
        msgs = session.exec(
            select(Message)
            .where(Message.chat_folder_id == chat_id)
            .order_by(Message.timestamp.asc())
        ).all()
    return [
        {
            "id": m.id,
            "role": "user" if m.role else "ai",
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
            "video_url": m.video_url  # ✅ tambahkan ini
        }
        for m in msgs
    ]
    
import subprocess, shlex, json
from pathlib import Path

#from AI.app import generate_educational_video  # pastikan ada __init__.py di folder AI


def generate_video_for_topic(topic: str) -> Optional[str]:
    """Placeholder - deploy AI separately"""
    return None

# def generate_video_for_topic(topic: str) -> Optional[str]:
#     """
#     Jalankan langsung fungsi generate_educational_video() dari AI/app.py
#     tanpa menggunakan subprocess. 
#     Mengembalikan URL video hasil upload ke Supabase.
#     """
#     try:
#         print(f"[EduGen] Generating educational video for topic: {topic}")

#         # Jalankan fungsi utama secara langsung
#         video_path, response = generate_educational_video(topic)

#         # Ambil URL dari hasil upload (Supabase)
#         video_url = response.get("video_path")
#         print(f"[EduGen] Video URL: {video_url}")

#         # Pastikan hasil valid
#         if video_url and "supabase.co" in video_url:
#             return video_url
#         else:
#             print("[EduGen] No Supabase URL found in response.")
#             return None

#     except Exception as e:
#         print(f"[EduGen ERROR] {e}")
#         return None
    
from langchain_google_genai import ChatGoogleGenerativeAI

def chat_with_gemini(user_message: str) -> str:
    """
    Mode chat biasa menggunakan Gemini.
    """
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    prompt = f"Kamu adalah asisten pembelajaran sains yang ramah. Jawab dengan jelas dan singkat.\n\n{user_message}"
    response = model.invoke(prompt)
    return response.content


@app.post("/api/chats/{chat_id}/messages")
def api_post_message(chat_id: int, payload: PostMessageIn, user: User = Depends(current_user_required)):
    with Session(engine) as session:
        # 🔍 Validasi chat
        chat = session.get(ChatFolder, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(status_code=404, detail="Not found")

        # 💬 Simpan pesan user
        user_msg = Message(chat_folder_id=chat.id, role=True, content=payload.content)
        session.add(user_msg)
        session.commit()
        session.refresh(user_msg)

        # 🎯 Deteksi apakah pesan mengandung perintah buat video
        # 💬 Mode chat biasa → pakai Gemini langsung
        ai_response = chat_with_gemini(payload.content)
        ai_msg = Message(chat_folder_id=chat.id, role=False, content=ai_response)
        session.add(ai_msg)
        session.commit()
        session.refresh(ai_msg)

        return {
            "ok": True,
            "mode": "chat",
            "user_message": {
                "id": user_msg.id,
                "role": "user",
                "content": user_msg.content,
                "timestamp": user_msg.timestamp.isoformat()
            },
            "ai_message": {
                "id": ai_msg.id,
                "role": "ai",
                "content": ai_msg.content,
                "timestamp": ai_msg.timestamp.isoformat()
            },
        }

        
from fastapi import APIRouter

@app.post("/api/chats/{chat_id}/generate_video")
def api_generate_video(chat_id: int, payload: dict, user: User = Depends(current_user_required)):
    """
    Endpoint dipanggil oleh tombol "Buat Video"
    Body JSON: {"topic": "Hukum Newton 1"}
    """
    topic = (payload.get("topic") or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")

    with Session(engine) as session:
        chat = session.get(ChatFolder, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # 💬 Simpan pesan user agar masuk ke database
        user_msg = Message(chat_folder_id=chat.id, role=True, content=topic)
        session.add(user_msg)
        session.commit()
        session.refresh(user_msg)
        
        
        # Simpan placeholder message
        ai_msg_processing = Message(chat_folder_id=chat.id, role=False, content=f"🎬 Generating video tentang '{topic}'...")
        session.add(ai_msg_processing)
        session.commit()

        # Jalankan generator video
        video_url = generate_video_for_topic(topic)

        ai_msg_done = Message(
            chat_folder_id=chat.id,
            role=False,
            content=f"✅ Video tentang '{topic}' berhasil dibuat!" if video_url else "❌ Maaf, video gagal dibuat.",
            video_url=video_url
        )
        session.add(ai_msg_done)
        session.commit()
        session.refresh(ai_msg_done)

    return {
        "ok": True,
        "topic": topic,
        "message": ai_msg_done.content,
        "video_url": ai_msg_done.video_url
    }        

class RenameChatIn(BaseModel):
    title: str

@app.patch("/api/chats/{chat_id}")
def api_rename_chat(
    chat_id: int,
    payload: RenameChatIn = Body(...),
    user: User = Depends(current_user_required),
):
    new_title = (payload.title or "").strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="Title required")

    with Session(engine) as session:
        chat = session.get(ChatFolder, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(status_code=404, detail="Not found")
        chat.title = new_title
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return {"ok": True, "id": chat.id, "title": chat.title}

@app.delete("/api/chats/{chat_id}")
def api_delete_chat(
    chat_id: int,
    user: User = Depends(current_user_required),
):
    with Session(engine) as session:
        chat = session.get(ChatFolder, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(status_code=404, detail="Not found")

        # Hapus semua message di chat ini (kalau ON DELETE CASCADE belum diset)
        session.exec(select(Message).where(Message.chat_folder_id == chat_id))
        session.query(Message).filter(Message.chat_folder_id == chat_id).delete()

        session.delete(chat)
        session.commit()
        return {"ok": True, "id": chat_id}


@app.get("/api/chats/search")
def api_search_chats(
    q: str = "",
    limit: int = 50,
    user: User = Depends(current_user_required),
):
    """
    Cari chat berdasarkan judul (milik user saat ini).
    GET /api/chats/search?q=...&limit=50
    Return: [{"id":..., "title":"..."}]
    """
    q = (q or "").strip()
    with Session(engine) as session:
        stmt = (
            select(ChatFolder)
            .where(ChatFolder.user_id == user.id)
            .order_by(ChatFolder.id.desc())
            .limit(limit)
        )
        if q:
            stmt = stmt.where(ChatFolder.title.ilike(f"%{q}%"))
        chats = session.exec(stmt).all()

    return [{"id": c.id, "title": c.title} for c in chats]