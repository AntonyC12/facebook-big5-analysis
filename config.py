import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
COOKIES_PATH = DATA_DIR / "cookies" / "fb_cookies.json"
RAW_DATA_PATH = DATA_DIR / "raw_json"
RESULTS_PATH = DATA_DIR / "results"

# Tiempos de espera aleatorios (en segundos)
WAIT_TIMES = {
    "micro": (0.5, 1.5),
    "short": (1, 3),
    "medium": (3, 7),
    "long": (5, 10),
    "extra_long": (10, 20)
}

# User-Agent realista
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Variables de entorno con valores por defecto
TARGET_PROFILE_URL = os.getenv("TARGET_PROFILE_URL", "https://facebook.com")
MAX_POSTS = int(os.getenv("MAX_POSTS", "50"))
HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "False").lower() == "true"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30000"))  # 30 segundos

# Configuración de análisis
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "10"))
SENTIMENT_THRESHOLD = float(os.getenv("SENTIMENT_THRESHOLD", "0.1"))

# Selectores de Facebook (actualizados 2024)
SELECTORS = {
    "post": "div[role='article']",
    "post_text": "div[data-ad-comet-preview='message'] span",
    "reactions": "[aria-label*='reacciones'], [aria-label*='reactions']",
    "comments": "a[aria-label*='comentario'], a[aria-label*='comment']",
    "profile_name": "h1",
    "bio": "div.bio, div.about, div.description",
    "friends": "a[href*='/friends']",
    "groups": "a[href*='/groups']"
}