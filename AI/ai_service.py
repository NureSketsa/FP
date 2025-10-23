from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app import generate_educational_video
import os

app = FastAPI()

class VideoRequest(BaseModel):
    topic: str
    complexity: str = "high-school"
    domain: str = "auto-detect"

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "EduGen AI"}

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    """Generate educational video"""
    try:
        video_path, response = generate_educational_video(
            topic=request.topic,
            complexity=request.complexity,
            domain=request.domain
        )
        
        return {
            "success": True,
            "video_url": response.get("video_path"),
            "metadata": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}