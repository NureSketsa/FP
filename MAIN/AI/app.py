""" 
Simple LEARNVIDAI function - Generate educational videos with a single function call
"""

import boto3
import os
from dotenv import load_dotenv
from pathlib import Path

# === Load .env dari beberapa kemungkinan lokasi ===
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent  # .../FP
main_dir = root_dir / "MAIN"

possible_envs = [
    current_dir / ".env",      # FP/AI/.env
    root_dir / ".env",         # FP/.env
    main_dir / ".env",         # FP/MAIN/.env
]

for env_path in possible_envs:
    if env_path.exists():
        print(f"✅ Loading environment from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        break
else:
    print("⚠️ No .env file found in AI/, MAIN/, or project root")
    
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional


from MAIN.AI.script_generator import ScienceVideoGenerator
from MAIN.AI.manim_code_generator import ManIMCodeGenerator
from MAIN.AI.animation_creator import create_animation_from_code


env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


def _get_video_storage_dir() -> Path:
    """
    Ambil folder penyimpanan video lokal dari env.
    Default: MAIN/videos relatif dari root project (FP).
    """
    base_dir = Path(__file__).resolve().parent  # .../FP/MAIN/AI
    project_root = base_dir.parent.parent      # .../FP

    env_value = os.getenv("VIDEO_FOLDER", "MAIN/videos")
    video_dir = Path(env_value)

    if not video_dir.is_absolute():
        video_dir = (project_root / video_dir).resolve()

    video_dir.mkdir(parents=True, exist_ok=True)
    return video_dir


def _move_video_to_storage(temp_video_path: str, final_name: str):
    """
    Upload ke Cloudflare R2 dan return public URL.
    """
    temp_video = Path(temp_video_path)

    if not temp_video.exists():
        raise FileNotFoundError("Video tidak ditemukan")

    r2 = boto3.client(
        "s3",
        endpoint_url=os.getenv("R2_ENDPOINT"),
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )

    bucket = os.getenv("R2_BUCKET_NAME")
    public_base = os.getenv("R2_BUCKET_PUBLIC_URL")

    # Upload file ke R2
    r2.upload_file(
        Filename=str(temp_video),
        Bucket=bucket,
        Key=final_name,
        ExtraArgs={"ContentType": "video/mp4"}
    )

    # Setelah upload, hapus file lokal
    temp_video.unlink()

    public_url = f"{public_base}/{final_name}"
    return public_url

def generate_educational_video(
    topic: str,
    complexity: str = "high-school",
    domain: str = "auto-detect",
    output_dir: str = "../MAIN/output",
    message_id: Optional[int] = None,
) -> Tuple[str, Dict]:
    import shutil
    from time import sleep

    BASE_DIR = Path(__file__).resolve().parent
    output_root = (BASE_DIR.parent / "MAIN" / "output").resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    # === Buat subfolder unik untuk topik ini ===
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:25]
    unique_output = output_root / f"{timestamp}_{safe_topic}"
    unique_output.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"🎓 LEARNVIDAI - Educational Video Generator")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Output folder: {unique_output}")
    print(f"{'='*60}\n")

    # === Step 1: Generate educational content ===
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    video_generator = ScienceVideoGenerator(google_api_key=api_key)
    prompt = f"Create an educational animation about {topic} for {complexity} level ({domain})."
    video_plan = video_generator.generate_complete_video_plan(prompt)
    if not video_plan or "error" in video_plan:
        raise Exception("Failed to generate educational content")
    print("✅ Educational content generated.")

    # === Step 2: Generate Manim code ===
    manim_generator = ManIMCodeGenerator(google_api_key=api_key)
    manim_code = manim_generator.generate_3b1b_manim_code(video_plan)
    print("✅ Animation code generated.")

    # === Step 3: Render video ke folder unik ===
    print("\n🎬 Rendering animation...")
    video_path = create_animation_from_code(manim_code, output_dir=str(unique_output))
    if not video_path or not os.path.exists(video_path):
        raise Exception("Failed to create animation")

    prefix = f"{message_id}_" if message_id is not None else ""
    new_video_name = f"{prefix}{timestamp}_{safe_topic}.mp4"
    new_video_path = unique_output / new_video_name
    os.rename(video_path, new_video_path)
    video_path = str(new_video_path)

    # === Pindahkan ke storage lokal dan buat URL publik ===
    print("\n💾 Menyimpan video ke storage lokal...")
    # stored_path, public_url = _move_video_to_storage(video_path, final_name=new_video_name)
    public_url = _move_video_to_storage(video_path, final_name=new_video_name)

    # 🧹 Hapus folder spesifik topik ini saja (folder sementara)
    shutil.rmtree(unique_output, ignore_errors=True)
    print(f"🧼 Deleted temp folder: {unique_output}")

    ai_response = {
        "topic": topic,
        "complexity": complexity,
        "domain": domain,
        "timestamp": timestamp,
        "video_path": None,   # absolute path di server (opsional)
        "video_url": public_url,     # URL publik untuk diakses frontend
        "educational_breakdown": video_plan.get("educational_breakdown", {}),
        "manim_structure": video_plan.get("manim_structure", {}),
        "generation_metadata": video_plan.get("generation_metadata", {}),
    }

    # Kembalikan URL publik sebagai nilai pertama
    # supaya kalau dipakai langsung untuk disimpan di DB,
    # yang tersimpan adalah path seperti: /learnvid-ai/static/videos/xxx.mp4
    return public_url, ai_response


def generate_video_for_topic_with_progress(topic: str, message_id: Optional[int] = None):
    """
    Modified version that yields progress updates
    """
    import shutil
    from time import sleep
    from pathlib import Path
    
    print(f"[DEBUG] Starting video generation for topic: '{topic}'")
    
    BASE_DIR = Path(__file__).resolve().parent
    output_root = (BASE_DIR.parent / "MAIN" / "output").resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    # === Buat subfolder unik untuk topik ini ===
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:25]
    unique_output = output_root / f"{timestamp}_{safe_topic}"
    unique_output.mkdir(parents=True, exist_ok=True)

    print(f"[DEBUG] Output folder: {unique_output}")

    try:
        # === Step 1: Generate educational content ===
        yield {"status": "generating_content", "message": "📝 Membuat konten edukatif..."}
        print("[DEBUG] Step 1: Starting educational content generation")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        video_generator = ScienceVideoGenerator(google_api_key=api_key)
        prompt = f"Create an educational animation about {topic}"
        
        print(f"[DEBUG] Generating video plan with prompt: {prompt}")
        video_plan = video_generator.generate_complete_video_plan(prompt)
        
        if not video_plan or "error" in video_plan:
            error_msg = f"Failed to generate educational content: {video_plan.get('error', 'Unknown error')}"
            print(f"[DEBUG ERROR] {error_msg}")
            raise Exception(error_msg)
        
        print("[DEBUG] Step 1 completed: Educational content generated")
        
        # === Step 2: Generate Manim code ===
        yield {"status": "generating_code", "message": "💻 Membuat kode animasi..."}
        print("[DEBUG] Step 2: Starting Manim code generation")
        
        manim_generator = ManIMCodeGenerator(google_api_key=api_key)
        manim_code = manim_generator.generate_3b1b_manim_code(video_plan)
        
        if not manim_code or len(manim_code.strip()) < 100:
            error_msg = "Generated Manim code is too short or empty"
            print(f"[DEBUG ERROR] {error_msg}")
            raise Exception(error_msg)
        
        print(f"[DEBUG] Step 2 completed: Manim code generated ({len(manim_code)} characters)")
        
        # === Step 3: Render video ===
        yield {"status": "rendering", "message": "🎬 Merender video..."}
        print("[DEBUG] Step 3: Starting video rendering")
        
        video_path = create_animation_from_code(manim_code, output_dir=str(unique_output))
        
        if not video_path or not os.path.exists(video_path):
            error_msg = f"Failed to create animation."
            print(f"[DEBUG ERROR] {error_msg}")
            raise Exception(error_msg)

        # [DEBUG 1] Check initial rendered file
        file_size = os.path.getsize(video_path)
        print(f"[DEBUG DETAIL] 1. Initial Video Found at: {video_path}")
        print(f"[DEBUG DETAIL]    Size: {file_size / (1024*1024):.2f} MB ({file_size} bytes)")
        if file_size == 0:
            print(f"[DEBUG ERROR] ⚠️ WARNING: Video file exists but is EMPTY (0 bytes)!")

        # Rename video file
        prefix = f"{message_id}_" if message_id is not None else ""
        new_video_name = f"{prefix}{timestamp}_{safe_topic}.mp4"
        new_video_path = unique_output / new_video_name

        print(f"[DEBUG] Renaming video to: {new_video_path}")
        os.rename(video_path, new_video_path)
        video_path = str(new_video_path)  # Update reference

        # [DEBUG 2] Check file after renaming
        if os.path.exists(video_path):
            print(f"[DEBUG DETAIL] 2. Rename Successful. File at: {video_path}")
        else:
            print(f"[DEBUG ERROR] ❌ LOST FILE after rename! Expected at: {video_path}")

        print("[DEBUG] Step 3 completed: Video rendered successfully")

        # === Step 4: Move to local storage ===
        yield {"status": "saving", "message": "💾 Menyimpan video ke server..."}
        print("[DEBUG] Step 4: Moving video to local storage")

        try:
            public_url = _move_video_to_storage(video_path, final_name=new_video_name)

            # cleanup
            shutil.rmtree(unique_output, ignore_errors=True)

        except Exception as storage_error:
            yield {"status": "error", "message": f"❌ {str(storage_error)}"}
            return

        yield {
            "status": "completed",
            "message": "✅ Video berhasil dibuat!",
            "video_url": public_url,
        }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[DEBUG EXCEPTION] {error_details}")
        yield {"status": "error", "message": f"❌ Error: {str(e)}"}
        
        # Cleanup on error
        try:
            if unique_output.exists():
                shutil.rmtree(unique_output, ignore_errors=True)
                print(f"[DEBUG] Cleaned up folder after error: {unique_output}")
        except:
            pass
        
import sys
# Example usage
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python3 run.py <topic> [complexity] [domain] [output_dir]")
        print("Example: python3 run.py 'Photosynthesis' high-school biology")
        sys.exit(1)

    topic = sys.argv[1]
    complexity = sys.argv[2] if len(sys.argv) > 2 else "high-school"
    domain = sys.argv[3] if len(sys.argv) > 3 else "auto-detect"
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "output"

    print(f"🚀 Running LEARNVIDAI for topic: {topic}")
    video_path, response = generate_educational_video(topic, complexity, domain, output_dir)

    print("\n📊 Results:")
    print(f"Video: {video_path}")
    print(f"Title: {response['educational_breakdown'].get('title', 'N/A')}")

    if response["educational_breakdown"].get("learning_objectives"):
        print("\nLearning Objectives:")
        for obj in response["educational_breakdown"]["learning_objectives"]:
            print(f"  • {obj}")
    
    
