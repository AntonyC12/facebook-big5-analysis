# config.py
import os
from pathlib import Path

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
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"