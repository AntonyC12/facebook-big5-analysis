# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
COOKIES_PATH = DATA_DIR / "cookies" / "fb_cookies.json"

# Tiempos de espera aleatorios entre acciones (en segundos)
WAIT_TIMES = {
    "short": (1, 3),
    "medium": (3, 7),
    "long": (5, 10)
}

# User agent para simular navegador real
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Configuración desde variables de entorno
TARGET_PROFILE_URL = os.getenv("TARGET_PROFILE_URL", "https://facebook.com")
MAX_POSTS = int(os.getenv("MAX_POSTS", "50"))
HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "False").lower() == "true"