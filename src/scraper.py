import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from config import (COOKIES_PATH, CREDENTIALS_PROVIDED, FACEBOOK_EMAIL,
                    FACEBOOK_PASSWORD, HEADLESS_BROWSER, MAX_POSTS, SELECTORS,
                    USER_AGENT, WAIT_TIMES)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacebookScraper:
    """Scraper optimizado de Facebook con login automático y manejo de errores"""

    def __init__(self, headless: Optional[bool] = None):
        self.headless = headless if headless is not None else HEADLESS_BROWSER
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.login_attempts = 0
        self.max_login_attempts = 2

    def __enter__(self):
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()

    def start_browser(self):
        """Inicia navegador con configuración optimizada"""
        logger.info("🚀 Iniciando navegador (headless=%s)...", self.headless)

        p = sync_playwright().start()

        self.browser = p.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            timeout=30000,  # 30 segundos timeout
        )

        self.context = self.browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="es-ES",
            timezone_id="America/Guayaquil",
            permissions=["geolocation"],
        )

        # Inyectar JavaScript para evadir detección
        self.context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['es-ES', 'es', 'en-US', 'en'] });
        """
        )

        self.page = self.context.new_page()
        self.page.set_default_timeout(15000)  # Timeout de 15 segundos por defecto

        logger.info("✅ Navegador listo")

    def close_browser(self):
        """Cierra el navegador y guarda cookies"""
        if self.browser:
            self.save_cookies()
            self.browser.close()
            logger.info("👋 Navegador cerrado")

    def random_wait(self, wait_type: str = "medium"):
        """Espera optimizada con tiempos reducidos"""
        min_wait, max_wait = WAIT_TIMES.get(wait_type, (1, 3))
        wait_time = random.uniform(min_wait, max_wait)
        time.sleep(wait_time)
        return wait_time

    def save_cookies(self):
        """Guarda cookies de sesión"""
        if self.context and self.page.url != "about:blank":
            cookies = self.context.cookies()
            COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(COOKIES_PATH, "w") as f:
                json.dump(cookies, f, indent=2)
            logger.info("💾 Cookies guardadas (%d cookies)", len(cookies))

    def load_cookies(self) -> bool:
        """Carga cookies existentes con validación"""
        if COOKIES_PATH.exists():
            try:
                with open(COOKIES_PATH, "r") as f:
                    cookies = json.load(f)

                if cookies and self.context:
                    self.context.add_cookies(cookies)

                    # Verificar que las cookies sean válidas
                    self.page.goto(
                        "https://facebook.com", wait_until="domcontentloaded"
                    )
                    self.random_wait("short")

                    if (
                        "facebook.com/home" in self.page.url
                        or self.page.locator(SELECTORS["email_input"]).count() == 0
                    ):
                        logger.info("🔑 Cookies válidas cargadas")
                        return True

            except Exception as e:
                logger.warning("⚠️ Error cargando cookies: %s", e)

        return False

    def automatic_login(self) -> bool:
        """
        Intenta login automático con credenciales
        Retorna True si tiene éxito
        """
        if not CREDENTIALS_PROVIDED:
            logger.warning("Credenciales no configuradas para login automático")
            return False

        logger.info("🔐 Intentando login automático...")

        try:
            # Ir a Facebook
            self.page.goto("https://facebook.com", wait_until="networkidle")
            self.random_wait("medium")

            # Rellenar email
            email_input = self.page.locator(SELECTORS["email_input"]).first
            if email_input.count() > 0:
                email_input.click()
                email_input.fill(FACEBOOK_EMAIL)
                self.random_wait("micro")

            # Rellenar password
            password_input = self.page.locator(SELECTORS["password_input"]).first
            if password_input.count() > 0:
                password_input.click()
                password_input.fill(FACEBOOK_PASSWORD)
                self.random_wait("micro")

            # Click en login
            login_button = self.page.locator(SELECTORS["login_button"]).first
            if login_button.count() > 0:
                login_button.click()
                self.random_wait("long")

            # Verificar login exitoso
            if any(
                x in self.page.url
                for x in ["facebook.com/home", "facebook.com/?sk=welcome"]
            ):
                logger.info("✅ Login automático exitoso")
                self.save_cookies()
                return True

            # Verificar si hay captcha o 2FA
            if (
                self.page.locator(
                    "text=/verifica tu identidad|security check/i"
                ).count()
                > 0
            ):
                logger.warning("⚠️ Se requiere verificación manual (2FA/Captcha)")
                return False

        except Exception as e:
            logger.error("❌ Error en login automático: %s", e)

        return False

    def ensure_login(self) -> bool:
        """
        Flujo optimizado de login:
        1. Cookies guardadas (más rápido)
        2. Login automático (si hay credenciales)
        3. Login manual (fallback)
        """
        logger.info("🔑 Iniciando proceso de autenticación...")

        # Intento 1: Cookies (más rápido, ~2 segundos)
        if self.load_cookies():
            logger.info("✅ Sesión restaurada desde cookies")
            return True

        # Intento 2: Login automático (si hay credenciales)
        if CREDENTIALS_PROVIDED and self.login_attempts < self.max_login_attempts:
            self.login_attempts += 1
            if self.automatic_login():
                return True

        # Intento 3: Login manual (solo si no está en headless)
        if not self.headless:
            logger.info("👤 Se requiere login manual...")
            return self.manual_login()
        else:
            logger.error("❌ No se pudo autenticar en modo headless")
            return False

    def manual_login(self) -> bool:
        """Login manual con interacción del usuario"""
        if self.headless:
            logger.error("❌ Login manual no disponible en modo headless")
            return False

        self.page.goto("https://facebook.com")
        self.random_wait("extra_long")

        print("\n" + "=" * 60)
        print("🔓 LOGIN MANUAL REQUERIDO")
        print("1. Haz login en la ventana del navegador")
        print("2. Espera a que cargue Facebook completamente")
        print("3. Vuelve aquí y presiona Enter")
        print("=" * 60 + "\n")

        input("Presiona Enter después del login...")

        # Verificar login
        if any(
            x in self.page.url
            for x in ["facebook.com/home", "facebook.com/?sk=welcome"]
        ):
            self.save_cookies()
            logger.info("✅ Login manual exitoso")
            return True

        logger.error("❌ Login manual falló")
        return False

    # ========== MÉTODOS OPTIMIZADOS DE EXTRACCIÓN ==========

    def extract_posts_optimized(self, max_posts: int = None) -> List[Dict]:
        """Extracción optimizada de posts con paralelización virtual"""
        if max_posts is None:
            max_posts = MAX_POSTS

        logger.info("📄 Extrayendo hasta %d posts (modo optimizado)...", max_posts)

        posts = []
        seen_texts = set()
        start_time = time.time()
        max_time = 120  # Máximo 2 minutos para scraping

        try:
            # Buscar contenedor de posts
            posts_container = self.page.locator(SELECTORS["posts_container"])
            if posts_container.count() == 0:
                logger.warning("No se encontró contenedor de posts")
                return posts

            # Scroll inteligente con detección de fin
            last_height = 0
            scroll_attempts = 0
            max_scrolls = 10

            while (
                len(posts) < max_posts
                and scroll_attempts < max_scrolls
                and (time.time() - start_time) < max_time
            ):

                # Extraer posts visibles en este momento
                current_posts = posts_container.locator(SELECTORS["post"])
                count = current_posts.count()

                for i in range(min(count, 20)):  # Procesar máximo 20 por iteración
                    if len(posts) >= max_posts:
                        break

                    try:
                        post = current_posts.nth(i)

                        # Extraer texto (con timeout corto)
                        text_elem = post.locator(SELECTORS["post_text"]).first
                        if text_elem.count() > 0:
                            text = text_elem.inner_text(timeout=2000).strip()
                        else:
                            continue

                        # Evitar duplicados
                        text_hash = hash(text[:100])
                        if text_hash in seen_texts:
                            continue

                        seen_texts.add(text_hash)

                        # Extraer reacciones rápidamente
                        reactions = 0
                        reactions_elem = post.locator(SELECTORS["reactions"]).first
                        if reactions_elem.count() > 0:
                            try:
                                reactions_text = (
                                    reactions_elem.get_attribute(
                                        "aria-label", timeout=1000
                                    )
                                    or ""
                                )
                                # Extraer número de reacciones
                                import re

                                match = re.search(r"(\d+)\s*[A-Za-z]", reactions_text)
                                if match:
                                    reactions = int(match.group(1))
                            except:
                                pass

                        posts.append(
                            {
                                "text": text,
                                "reactions": reactions,
                                "timestamp": time.time(),
                                "length": len(text),
                            }
                        )

                    except Exception as e:
                        logger.debug("Error procesando post %d: %s", i, e)
                        continue

                # Scroll inteligente
                new_height = self.page.evaluate("document.documentElement.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0

                last_height = new_height

                # Scroll con variación aleatoria
                scroll_amount = random.randint(800, 1500)
                self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                self.random_wait("short")

        except Exception as e:
            logger.error("Error en extract_posts_optimized: %s", e)

        logger.info(
            "✅ %d posts extraídos en %.1f segundos",
            len(posts),
            time.time() - start_time,
        )
        return posts

    def extract_profile_info_optimized(self) -> Dict:
        """Extracción rápida de información del perfil"""
        logger.info("📋 Extrayendo información del perfil...")

        info = {"url": self.page.url}
        start_time = time.time()

        try:
            # Nombre (con timeout corto)
            name_elem = self.page.locator(SELECTORS["profile_name"]).first
            if name_elem.count() > 0:
                info["name"] = name_elem.inner_text(timeout=3000).strip()

            # Biografía (opcional)
            bio_elem = self.page.locator(SELECTORS["bio"]).first
            if bio_elem.count() > 0:
                info["bio"] = bio_elem.inner_text(timeout=2000).strip()

            # Intentar extraer amigos rápidamente
            try:
                friends_elem = self.page.locator(SELECTORS["friends_link"]).first
                if friends_elem.count() > 0:
                    friends_text = friends_elem.inner_text(timeout=1000)
                    # Buscar número en el texto
                    import re

                    match = re.search(r"(\d+[\s,]*\d*)", friends_text)
                    if match:
                        info["friends_text"] = match.group(1)
            except:
                pass

        except Exception as e:
            logger.warning("Error extrayendo info del perfil: %s", e)

        logger.debug("Info extraída en %.2f segundos", time.time() - start_time)
        return info
