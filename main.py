# main.py (actualizado)
import json
import time
from pathlib import Path
from src.scraper import FacebookScraper
from src.personality import BigFiveAnalyzer

def scrape_facebook_data(profile_url: str, use_cookies: bool = True):
    """Extrae datos de Facebook y los guarda en JSON."""
    print("Iniciando scraper de Facebook...")

    with FacebookScraper(headless=False) as scraper:
        # Intentar cargar cookies existentes
        if use_cookies:
            cookies_loaded = scraper.load_cookies()
            if not cookies_loaded:
                print("No se encontraron cookies. Se requiere login manual.")
                scraper.login_manually()
        else:
            print("Login manual requerido (sin cookies)...")
            scraper.login_manually()

        # Navegar al perfil objetivo
        print(f"Navegando al perfil: {profile_url}")
        scraper.navigate_to_profile(profile_url)
        time.sleep(3)

        # Extraer datos
        print("Extrayendo información del perfil...")
        data = {}

        data["basic_info"] = scraper.extract_basic_info()
        print(f"  - Nombre: {data['basic_info'].get('name', 'No encontrado')}")

        print("Extrayendo publicaciones (esto puede tomar unos minutos)...")
        data["posts"] = scraper.extract_posts(max_posts=50)
        print(f"  - {len(data['posts'])} publicaciones extraídas")

        print("Extrayendo información de amigos...")
        data["friends_count"] = scraper.extract_friends_count()
        print(f"  - {data['friends_count']} amigos detectados")

        print("Extrayendo grupos...")
        data["groups"] = scraper.extract_groups()
        print(f"  - {len(data['groups'])} grupos encontrados")

        data["extraction_timestamp"] = time.time()

        return data

def analyze_personality(data: Dict):
    """Analiza los datos y devuelve un reporte de personalidad."""
    print("\nAnalizando personalidad Big Five...")

    analyzer = BigFiveAnalyzer()

    # Calcular scores
    scores = analyzer.calculate_big_five_scores(data)
    report = analyzer.generate_personality_report(scores)

    # Análisis de sentimiento adicional
    posts_text = [post.get("text", "") for post in data.get("posts", [])]
    sentiment = analyzer.analyze_text_sentiment(posts_text)

    analysis_result = {
        "big_five_scores": scores,
        "personality_report": report,
        "sentiment_analysis": sentiment,
        "metadata": {
            "total_posts_analyzed": len(data.get("posts", [])),
            "total_words_analyzed": sum(len(post.get("text", "").split()) for post in data.get("posts", [])),
            "analysis_timestamp": time.time()
        }
    }

    return analysis_result

def save_results(data: Dict, analysis: Dict, output_dir: Path):
    """Guarda los datos y análisis en archivos JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Guardar datos crudos
    raw_data_path = output_dir / "raw_data.json"
    with open(raw_data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Guardar análisis
    analysis_path = output_dir / "personality_analysis.json"
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # Guardar reporte en texto plano
    report_path = output_dir / "personality_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== REPORTE DE PERSONALIDAD BIG FIVE ===\n\n")
        f.write(analysis["personality_report"])
        f.write("\n\n=== ANÁLISIS DE SENTIMIENTO ===\n")
        f.write(f"Publicaciones positivas: {analysis['sentiment_analysis']['positive']}\n")
        f.write(f"Publicaciones negativas: {analysis['sentiment_analysis']['negative']}\n")
        f.write(f"Publicaciones neutrales: {analysis['sentiment_analysis']['neutral']}\n")
        f.write(f"Polaridad promedio: {analysis['sentiment_analysis']['avg_polarity']:.3f}\n")

    return raw_data_path, analysis_path, report_path

def main():
    # Configuración
    TARGET_PROFILE = "https://www.facebook.com/tu_perfil_principal"  # CAMBIAR
    OUTPUT_DIR = Path("data/results")

    print("=" * 60)
    print("ANÁLISIS DE PERSONALIDAD BIG FIVE - FACEBOOK")
    print("=" * 60)

    try:
        # Paso 1: Scraping
        data = scrape_facebook_data(TARGET_PROFILE)

        # Paso 2: Análisis
        analysis = analyze_personality(data)

        # Paso 3: Guardar resultados
        raw_path, analysis_path, report_path = save_results(data, analysis, OUTPUT_DIR)

        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\nResultados guardados en:")
        print(f"  - Datos crudos: {raw_path}")
        print(f"  - Análisis JSON: {analysis_path}")
        print(f"  - Reporte texto: {report_path}")

        print(f"\nPuntuaciones Big Five:")
        for trait, score in analysis["big_five_scores"].items():
            print(f"  - {trait.capitalize()}: {score:.3f}")

        print(f"\nReporte de personalidad:\n{analysis['personality_report']}")

    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()