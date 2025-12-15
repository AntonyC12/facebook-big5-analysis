# main.py
import json
from pathlib import Path
from src.scraper import FacebookScraper

def main():
    # URL del perfil objetivo (tu cuenta principal)
    TARGET_PROFILE = "https://www.facebook.com/tu_perfil_principal"

    print("Iniciando scraper de Facebook para análisis Big Five...")

    with FacebookScraper(headless=False) as scraper:
        # 1. Intentar cargar cookies existentes
        cookies_loaded = scraper.load_cookies()

        # 2. Si no hay cookies, hacer login manual
        if not cookies_loaded:
            print("No se encontraron cookies. Se requiere login manual.")
            scraper.login_manually()

        # 3. Navegar al perfil objetivo
        print(f"Navegando al perfil: {TARGET_PROFILE}")
        scraper.navigate_to_profile(TARGET_PROFILE)

        # 4. Extraer datos
        print("Extrayendo información básica...")
        basic_info = scraper.extract_basic_info()

        print("Extrayendo publicaciones...")
        posts = scraper.extract_posts(max_posts=30)

        print("Extrayendo información de amigos...")
        friends_count = scraper.extract_friends_count()

        print("Extrayendo grupos...")
        groups = scraper.extract_groups()

        # 5. Guardar datos en JSON
        data = {
            "basic_info": basic_info,
            "posts": posts,
            "friends_count": friends_count,
            "groups": groups,
            "extraction_timestamp": time.time()
        }

        output_path = Path("data/raw_json/extracted_data.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Datos guardados en {output_path}")
        print(f"Resumen: {len(posts)} posts, {friends_count} amigos, {len(groups)} grupos")

if __name__ == "__main__":
    import time
    main()