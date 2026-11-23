from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Load .env specifically from BASE_DIR if it exists
env_path = BASE_DIR / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "scout.db"))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "python")

