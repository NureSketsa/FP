"""
Simple LEARNVIDAI function - Generate educational videos with a single function call
"""


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
from typing import Dict, Tuple


from MAIN.AI.script_generator import ScienceVideoGenerator
from MAIN.AI.manim_code_generator import ManIMCodeGenerator
from MAIN.AI.animation_creator import create_animation_from_code

from supabase import create_client
import mimetypes

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def upload_to_supabase(file_path: str, bucket_name: str = "videos") -> str:
    """
    Upload video ke Supabase Storage dan kembalikan URL publik.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials (SUPABASE_URL / SUPABASE_KEY) tidak ditemukan")

    supabase = create_client(url, key)
    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        res = supabase.storage.from_(bucket_name).upload(file_name, f, {"content-type": mimetypes.guess_type(file_name)[0]})
    
    # Jika bucket public:
    public_url = f"{url}/storage/v1/object/public/{bucket_name}/{file_name}"
    return public_url


def generate_educational_video(
    topic: str,
    complexity: str = "high-school",
    domain: str = "auto-detect",
    output_dir: str = "../MAIN/output"
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

    new_video_name = f"{timestamp}_{safe_topic}.mp4"
    new_video_path = unique_output / new_video_name
    os.rename(video_path, new_video_path)
    video_path = str(new_video_path)

    # === Upload ke Supabase ===
    print("\n☁️ Uploading to Supabase Storage...")
    supabase_url = None
    try:
        supabase_url = upload_to_supabase(video_path)
        print(f"{supabase_url}")

        # Tunggu sebentar agar proses file selesai
        sleep(2)

        # 🧹 Hapus folder spesifik topik ini saja
        shutil.rmtree(unique_output, ignore_errors=True)
        print(f"🧼 Deleted local folder: {unique_output}")

    except Exception as e:
        print(f"❌ Upload gagal: {e}")

    ai_response = {
        "topic": topic,
        "complexity": complexity,
        "domain": domain,
        "timestamp": timestamp,
        "video_path": supabase_url or video_path,
        "educational_breakdown": video_plan.get("educational_breakdown", {}),
        "manim_structure": video_plan.get("manim_structure", {}),
        "generation_metadata": video_plan.get("generation_metadata", {}),
    }

    return video_path, ai_response

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
    
    

