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
        self.is_logged_in = False

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
            self.is_logged_in = True
            return True
        return False

    def ensure_login(self):
        """Asegura que el scraper está logueado, usando cookies o login manual."""
        if not self.load_cookies():
            self.login_manually()
        else:
            print("Sesión restaurada desde cookies.")

    def login_manually(self, url: str = "https://www.facebook.com"):
        """
        Navega a Facebook y espera login manual.
        Guarda cookies después del login.
        """
        self.page.goto(url)
        self.random_wait("long")

        # Esperar que el usuario haga login manualmente
        print("="*60)
        print("Por favor, haz login manualmente en el navegador.")
        print("Después de iniciar sesión, regresa aquí y presiona Enter.")
        print("="*60)
        input("Presiona Enter después de iniciar sesión...")

        # Guardar cookies después del login
        self.save_cookies()
        self.is_logged_in = True
        print("Login manual completado y cookies guardadas.")

    def scrape_profile_basic_info(self, profile_url: str) -> Dict:
        """Extrae información básica del perfil."""
        self.navigate_to_profile(profile_url)
        return self.extract_basic_info()

    def navigate_to_profile(self, profile_url: str):
        """Navega al perfil deseado con esperas aleatorias."""
        self.page.goto(profile_url)
        self.random_wait("long")

    def extract_basic_info(self) -> Dict:
        """Extrae información básica del perfil."""
        self.random_wait("short")
        # Selectores mejorados
        try:
            # Intentar obtener el nombre del perfil
            name = self.page.locator("h1").first.inner_text(timeout=5000)
        except:
            name = ""

        try:
            # Intentar obtener la biografía
            bio = self.page.locator("div.bio, div.about, div.description").first.inner_text(timeout=5000)
        except:
            bio = ""

        return {
            "name": name.strip() if name else "",
            "bio": bio.strip() if bio else "",
            "profile_url": self.page.url
        }

    def scrape_posts(self, max_posts: int = 50) -> List[Dict]:
        """Extrae publicaciones del muro."""
        return self.extract_posts(max_posts)

    def extract_posts(self, max_posts: int = 50) -> List[Dict]:
        """Extrae publicaciones del muro."""
        posts = []
        scroll_attempts = 0
        max_scroll_attempts = 20

        while len(posts) < max_posts and scroll_attempts < max_scroll_attempts:
            # Encontrar elementos de publicaciones
            post_elements = self.page.locator("div[role='article']").all()

            for post in post_elements:
                if len(posts) >= max_posts:
                    break

                try:
                    # Extraer texto (selector necesita ajuste)
                    text_elem = post.locator("span:has-text('')").first
                    text = text_elem.inner_text(timeout=3000) if text_elem.count() > 0 else ""

                    # Extraer reacciones aproximadas
                    reactions = post.locator("div[aria-label*='reactions']").count()

                    # Extraer comentarios aproximados
                    comments = post.locator("div[aria-label*='comment']").count()

                    posts.append({
                        "text": text,
                        "reactions": reactions,
                        "comments": comments,
                        "timestamp": time.time()
                    })
                except Exception as e:
                    print(f"Error extrayendo post: {e}")

            # Scroll down
            self.page.mouse.wheel(0, random.randint(1000, 3000))
            self.random_wait("medium")
            scroll_attempts += 1

        return posts

    def extract_friends_count(self) -> int:
        """Extrae el número de amigos (si es visible)."""
        try:
            # Navegar a la sección de amigos
            friends_url = self.page.url.rstrip('/') + "/friends"
            self.page.goto(friends_url)
            self.random_wait("medium")

            # Contar elementos de amigos (selector aproximado)
            friend_elements = self.page.locator("div.friend, div[data-testid='friend_list_item']").count()
            return friend_elements
        except Exception as e:
            print(f"Error extrayendo amigos: {e}")
            return 0

    def extract_groups(self) -> List[str]:
        """Extrae grupos a los que pertenece (si son visibles)."""
        try:
            groups_url = self.page.url.rstrip('/') + "/groups"
            self.page.goto(groups_url)
            self.random_wait("medium")

            groups = []
            group_elements = self.page.locator("div.group, div[data-testid='group_item']").all()

            for group in group_elements:
                name = group.inner_text(timeout=3000)
                if name:
                    groups.append(name.strip())

            return groups
        except Exception as e:
            print(f"Error extrayendo grupos: {e}")
            return []