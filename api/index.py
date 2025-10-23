import sys
from pathlib import Path

# Add MAIN directory to Python path
main_dir = Path(__file__).parent.parent / "MAIN"
sys.path.insert(0, str(main_dir))

from MAIN import app

# Vercel expects 'app' or 'handler'
handler = app