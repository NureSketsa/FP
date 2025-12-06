import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, URLSafeSerializer
from langchain_google_genai import ChatGoogleGenerativeAI
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine, select

from MAIN.AI.app import generate_educational_video, generate_video_for_topic_with_progress

# === Load .env dari lokasi AI, MAIN, atau root ===
BASE_DIR = Path(__file__).resolve().parent       # .../FP/MAIN
project_root = BASE_DIR.parent                   # .../FP
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


def _title_from_video_url(video_url: str | None) -> str:
    """
    Ekstrak judul video dari format nama file baru:
      {msgId}_{tanggal}_{waktu}_{title}.mp4
    Contoh:
      76_20251130_222549_newton_2.mp4 -> "Newton 2"
    """
    if not video_url:
        return "Untitled Video"

    filename = os.path.basename(video_url).split("?", 1)[0]
    name, _ = os.path.splitext(filename)

    # Pecah menjadi 4 bagian:
    # [msgId, tanggal, waktu, title]
    parts = name.split("_", 3)
    if len(parts) < 4:
        # Format lama atau tidak sesuai → fallback ke versi simple
        cleaned = name.replace("_", " ").strip()
        return cleaned.title() if cleaned else "Untitled Video"

    title_part = parts[3]  # ambil bagian title

    # Ubah underscore → spasi, kapitalisasi tiap kata
    cleaned = title_part.replace("_", " ").strip()
    return cleaned.title() if cleaned else "Untitled Video"

# ---------------- App ----------------
# app = FastAPI()
app = FastAPI(root_path="/learnvid-ai")
# app = FastAPI(root_path="/learnvid-ai")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
from fastapi.staticfiles import StaticFiles

# Static untuk asset biasa
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# app.mount("/learnvid-ai/static", StaticFiles(directory="MAIN/static"), name="static")

# # Static untuk video lokal
# video_folder_env = os.getenv("VIDEO_FOLDER", "MAIN/videos")
# video_dir = Path(video_folder_env)
# if not video_dir.is_absolute():
#     video_dir = (project_root / video_dir).resolve()
# video_dir.mkdir(parents=True, exist_ok=True)
# # app.mount("/videos", StaticFiles(directory=str(video_dir)), name="videos")

VIDEO_DIR = (BASE_DIR / "static" / "videos").resolve()
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

video_dir = VIDEO_DIR  # agar kode lain tetap jalan


from fastapi.responses import FileResponse
from pathlib import Path

# video_dir = Path("MAIN/videos").resolve()

# @app.get("/videos/{filename}")
# async def get_video(filename: str):
#     file_path = video_dir / filename
#     if not file_path.exists():
#         return {"detail": "Video not found"}

#     return FileResponse(path=str(file_path), media_type="video/mp4")



@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Redirect user to home (/) for 401 errors on HTML pages,
    but keep JSON response for API endpoints.
    """
    # Untuk endpoint API, tetap kembalikan JSON default
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)

    # Jika unauthorized saat akses halaman biasa → redirect ke beranda
    if exc.status_code == 401:
        return RedirectResponse(url="/learnvid-ai/", status_code=303)

    # Selain itu, gunakan handler default
    return await http_exception_handler(request, exc)

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

from fastapi.responses import FileResponse
# ---------------- Pages ----------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/faq", response_class=HTMLResponse)
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/how-it-works", response_class=HTMLResponse)
def how_it_works_page(request: Request):
    return templates.TemplateResponse("how-it-works.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": None})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})

@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/learnvid-ai/", status_code=303)   # >>> changed
    clear_session(resp)
    return resp

@app.get("/gallery", response_class=HTMLResponse)
def gallery_page(request: Request, user: User = Depends(current_user_required)):
    with Session(engine) as session:
        chat_list = session.exec(
            select(ChatFolder)
            .where(ChatFolder.user_id == user.id)
            .order_by(ChatFolder.id.desc())
        ).all()

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "username": user.username,
            "chats": chat_list
        }
    )

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
def reviews_page(request: Request):
    return templates.TemplateResponse("reviews.html", {"request": request, "message": None})

@app.get("/api/gallery/videos")
def api_gallery_videos(user: User = Depends(current_user_required)):
    with Session(engine) as session:
        # Ambil semua chat folder milik user
        chat_ids = session.exec(
            select(ChatFolder.id).where(ChatFolder.user_id == user.id)
        ).all()

        # Ambil semua message yang punya video_url
        videos = session.exec(
            select(Message)
            .where(Message.chat_folder_id.in_(chat_ids))
            .where(Message.video_url.is_not(None))
            .order_by(Message.timestamp.desc())
        ).all()

    return [
        {
            "id": v.id,
            "video_url": v.video_url,
            "content": v.content,
            "title": _title_from_video_url(v.video_url),
            "timestamp": v.timestamp.isoformat(),
        }
        for v in videos
    ]


@app.post("/api/reviews")
def submit_review(data: dict):
    """Terima review dari form frontend (AJAX POST)"""
    try:
        nama = data.get("nama", "").strip()
        email_raw = (data.get("email") or "").strip()
        # Backend historically memakai field nrp & kelompok.
        # Form baru mengirim email & instansi, jadi kita map ke kolom lama.
        nrp = (data.get("nrp") or email_raw or "").strip()
        kelompok = (data.get("kelompok") or data.get("instansi") or "").strip()
        rating = int(data.get("rating", 0))
        review_text = data.get("review", "").strip()

        # Basic email format check
        if not email_raw or "@" not in email_raw or "." not in email_raw.split("@")[-1]:
            raise HTTPException(status_code=400, detail="Invalid email format")

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
                    # Alias untuk frontend baru:
                    "email": new_review.nrp,
                    "instansi": new_review.kelompok,
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
            # Alias agar JS di reviews.html bisa pakai email & instansi
            "email": r.nrp,
            "instansi": r.kelompok,
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
    resp = RedirectResponse(url="/learnvid-ai/chat", status_code=303)
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
    resp = RedirectResponse(url="/learnvid-ai/chat", status_code=303)
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
def generate_video_for_topic(topic: str) -> Optional[str]:
    """
    Jalankan langsung fungsi generate_educational_video() dari AI/app.py
    tanpa menggunakan subprocess. 
    Mengembalikan URL video (lokal) yang bisa diakses frontend.
    """
    try:
        print(f"[learnvidai] Generating educational video for topic: {topic}")

        # Jalankan fungsi utama secara langsung
        video_path, response = generate_educational_video(topic)

        # Ambil URL publik dari response (lokal)
        video_url = response.get("video_url") or response.get("video_path")
        print(f"[learnvidai] Video URL: {video_url}")

        # Pastikan hasil valid (string non-kosong)
        if video_url:
            return video_url
        else:
            print("[learnvidai] No video URL found in response.")
            return None

    except Exception as e:
        print(f"[learnvidai ERROR] {e}")
        return None
def chat_with_gemini(user_message: str) -> str:
    """
    Mode chat biasa menggunakan Gemini.
    """
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

    prompt = f"""
    Kamu adalah asisten pembelajaran sains yang ramah. Jawab dengan jelas dan singkat.\n\n{user_message}
    """
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
    Endpoint with SSE streaming for progress updates (SYNC version)
    """
    topic = (payload.get("topic") or "").strip()
    print(f"[API DEBUG] Received topic: '{topic}'")
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")

    with Session(engine) as session:
        chat = session.get(ChatFolder, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        user_msg = Message(chat_folder_id=chat.id, role=True, content=topic)
        session.add(user_msg)
        session.commit()
        session.refresh(user_msg)  # untuk dapatkan ID pesan user

    def generate_with_progress():
        """Synchronous generator function
        
        Menyimpan hanya SATU baris progress di tabel messages
        untuk proses pembuatan video ini. Setiap update progress
        akan mengubah isi baris tersebut agar yang tersimpan
        selalu status progress terkini.
        """
        # ID message progress (AI) yang sedang berjalan untuk chat & request ini
        progress_msg_id: Optional[int] = None

        try:
            yield f": {' ' * 4096}\n\n"
            initial_msg = {'status': 'started', 'message': f'🎬 Memulai pembuatan video tentang {topic}...'}
            yield f"data: {json.dumps(initial_msg)}\n\n"

            # 💾 Simpan / update progress awal ke DB (hanya 1 baris)
            try:
                with Session(engine) as session:
                    if progress_msg_id is None:
                        progress_msg = Message(
                            chat_folder_id=chat_id,
                            role=False,
                            # Simpan hanya teks pesan tanpa prefix status
                            content=initial_msg["message"],
                        )
                        session.add(progress_msg)
                        session.commit()
                        session.refresh(progress_msg)
                        progress_msg_id = progress_msg.id
                    else:
                        progress_msg = session.get(Message, progress_msg_id)
                        if progress_msg:
                            progress_msg.content = initial_msg["message"]
                            session.add(progress_msg)
                            session.commit()
            except Exception as db_err:
                print(f"[PROGRESS DB ERROR] {db_err}")
            
            video_url = None
            has_error = False
            error_text = None
            
            for progress in generate_video_for_topic_with_progress(topic, message_id=user_msg.id):
                print(f"[STREAM] Progress: {progress}")
                yield f"data: {json.dumps(progress)}\n\n"

                # 💾 Simpan setiap progress penting ke DB (update baris yang sama)
                try:
                    status = progress.get("status")
                    message_text = progress.get("message") or ""

                    # Simpan hanya status utama agar tidak terlalu bising
                    if status in {"generating_content", "generating_code", "rendering", "saving", "error"} and message_text:
                        with Session(engine) as session:
                            if progress_msg_id is None:
                                progress_msg = Message(
                                    chat_folder_id=chat_id,
                                    role=False,
                                    # Simpan hanya teks progress tanpa prefix status
                                    content=message_text,
                                )
                                session.add(progress_msg)
                                session.commit()
                                session.refresh(progress_msg)
                                progress_msg_id = progress_msg.id
                            else:
                                progress_msg = session.get(Message, progress_msg_id)
                                if progress_msg:
                                    progress_msg.content = message_text
                                    session.add(progress_msg)
                                    session.commit()
                except Exception as db_err:
                    print(f"[PROGRESS DB ERROR] {db_err}")
                
                if progress.get('status') == 'completed':
                    video_url = progress.get('video_url')
                if progress.get('status') == 'error':
                    has_error = True
                    error_text = progress.get('message')
            
            if not has_error and video_url:
                with Session(engine) as session:
                    ai_msg = Message(
                        chat_folder_id=chat_id,
                        role=False,
                        content=f"✅ Video tentang '{topic}' berhasil dibuat!",
                        video_url=video_url
                    )
                    session.add(ai_msg)
                    session.commit()
                    session.refresh(ai_msg)
                    
                    yield f"data: {json.dumps({'status': 'done', 'message': ai_msg.content, 'video_url': video_url, 'message_id': ai_msg.id})}\n\n"
            elif has_error:
                # Simpan pesan error ke database agar tidak temporary
                with Session(engine) as session:
                    ai_msg = Message(
                        chat_folder_id=chat_id,
                        role=False,
                        content=error_text or "❌ Maaf, terjadi kesalahan. Coba lagi nanti.",
                        video_url=None
                    )
                    session.add(ai_msg)
                    session.commit()
                    session.refresh(ai_msg)

                    yield f"data: {json.dumps({'status': 'final_error', 'message': ai_msg.content, 'message_id': ai_msg.id})}\n\n"
        
        except Exception as e:
            import traceback
            print(f"[STREAM ERROR] {traceback.format_exc()}")
            yield f"data: {json.dumps({'status': 'error', 'message': f'❌ Error: {str(e)}'})}\n\n"

    # Gunakan StreamingResponse untuk SSE (Server-Sent Events)
    # Tambah header anti-buffering agar reverse proxy (mis. nginx di kampus)
    # tidak menahan output sampai selesai, sehingga progress bisa tampil live.
    return StreamingResponse(
        generate_with_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Beberapa setup nginx menghormati header ini untuk mematikan buffering
            "X-Accel-Buffering": "no",
        },
    )

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

@app.get("/api/download")
async def proxy_download(url: str):
    import httpx
    
    # Extract filename from URL
    original_name = url.split("/")[-1]

    # Example: 446_20251206_152930_fisika_smp.mp4
    name_without_ext, ext = original_name.rsplit(".", 1)

    # Split into 4 parts: id, date, time, title
    parts = name_without_ext.split("_", 3)

    if len(parts) == 4:
        title_raw = parts[3]  # → "fisika_smp"
        download_name = title_raw.replace("_", " ").strip() + "." + ext
    else:
        # fallback: remove numbers & cleanup
        download_name = name_without_ext.replace("_", " ").strip() + "." + ext

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(404, "File not found")

        return Response(
            content=r.content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{download_name}"'
            }
        )