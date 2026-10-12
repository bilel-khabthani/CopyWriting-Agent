import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip().rstrip("/")
MODEL = os.getenv("MODEL", "qwen2.5:3b").strip()
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "qwen2.5-coder:3b").strip()

STRATEGIST_TEMPERATURE = 0.3
WRITER_TEMPERATURE = 0.8

NUM_CTX = 8192
NUM_PREDICT = 1024
REQUEST_TIMEOUT = 180.0
KEEP_ALIVE = "10m"

LOG_FILE = "bot.log"

_raw_ids = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = [
    int(part)
    for part in _raw_ids.replace(";", ",").split(",")
    if part.strip().isdigit()
]
