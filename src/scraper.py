# src/scraper.py
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext

from config import COOKIES_PATH, WAIT_TIMES, USER_AGENT

class FacebookScraper:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()

    def start_browser(self):
        """Inicia el navegador con configuración personalizada."""
        p = sync_playwright().start()
        self.browser = p.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()

    def close_browser(self):
        """Cierra el navegador."""
        if self.browser:
            self.browser.close()

    def random_wait(self, wait_type: str = "medium"):
        """Espera un tiempo aleatorio entre acciones."""
        min_wait, max_wait = WAIT_TIMES.get(wait_type, (2, 5))
        time.sleep(random.uniform(min_wait, max_wait))

    def save_cookies(self):
        """Guarda las cookies de la sesión actual en un archivo JSON."""
        if self.context:
            cookies = self.context.cookies()
            COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(COOKIES_PATH, 'w') as f:
                json.dump(cookies, f)
            print(f"Cookies guardadas en {COOKIES_PATH}")

    def load_cookies(self):
        """Carga cookies desde archivo si existen."""
        if COOKIES_PATH.exists():
            with open(COOKIES_PATH, 'r') as f:
                cookies = json.load(f)
                if self.context:
                    self.context.add_cookies(cookies)
            print("Cookies cargadas exitosamente")
            return True
        return False

    def login_manually(self, url: str = "https://www.facebook.com"):
        """
        Navega a Facebook y espera login manual.
        Guarda cookies después del login.
        """
        self.page.goto(url)
        self.random_wait("long")

        # Esperar que el usuario haga login manualmente
        input("Por favor, haz login manualmente en el navegador y luego presiona Enter aquí...")

        # Guardar cookies después del login
        self.save_cookies()
        print("Login manual completado y cookies guardadas.")