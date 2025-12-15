# main.py - ACTUALIZADO
import sys
import time

from config import HEADLESS_BROWSER, MAX_POSTS, TARGET_PROFILE_URL
from src.personality import BigFiveAnalyzer
from src.scraper import FacebookScraper
from src.utils import format_duration, save_json


def main():
    print("🚀 INICIANDO ANÁLISIS DE PERSONALIDAD BIG FIVE (ESPAÑOL)")
    print("=" * 60)
    print("🌐 Idioma de análisis: ESPAÑOL")
    print(f"📁 Perfil objetivo: {TARGET_PROFILE_URL}")
    print("=" * 60)

    start_time = time.time()

    try:
        # FASE 1: Scraping
        print("\n🔍 Fase 1: Scraping de datos...")
        scrape_start = time.time()

        with FacebookScraper(headless=HEADLESS_BROWSER) as scraper:
            # Login
            if not scraper.ensure_login():
                print("❌ Falló la autenticación")
                sys.exit(1)

            # Navegar al perfil
            scraper.page.goto(TARGET_PROFILE_URL, wait_until="domcontentloaded")
            scraper.random_wait("medium")

            # Extraer datos
            profile_info = scraper.extract_profile_info_optimized()
            posts = scraper.extract_posts_optimized(MAX_POSTS)

            # Datos para análisis
            sample_data = {
                "basic_info": profile_info,
                "posts": posts,
                "friends_count": 0,  # Placeholder - implementar extract_friends_count()
                "groups": [],  # Placeholder - implementar extract_groups()
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "scraping_duration": time.time() - scrape_start,
                "language_detected": "es",  # Añadimos detección de idioma
            }

        print(
            f"✅ Scraping completado en {format_duration(time.time() - scrape_start)}"
        )
        print(f"   📄 Posts en español obtenidos: {len(posts)}")

        # FASE 2: Análisis Big Five en español
        print("\n🧠 Fase 2: Análisis Big Five (ESPAÑOL)...")
        analysis_start = time.time()

        analyzer = BigFiveAnalyzer()
        scores = analyzer.calculate_big_five_scores(sample_data)
        report = analyzer.generate_personality_report(scores)

        print(
            f"✅ Análisis en español completado en {format_duration(time.time() - analysis_start)}"
        )

        # FASE 3: Resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS BIG FIVE (ANÁLISIS EN ESPAÑOL):")
        print("=" * 60)
        print(report)
        print("=" * 60)

        # Mostrar detalles del análisis en español
        metadata = analyzer.results["metadata"]
        print(f"\n📈 METADATOS DEL ANÁLISIS EN ESPAÑOL:")
        print(f"   • Publicaciones analizadas: {metadata['posts_analyzed']}")
        print(f"   • Palabras totales en español: {metadata['words_analyzed']:,}")
        print(f"   • Palabras únicas en español: {metadata['unique_words']:,}")
        print(f"   • Diversidad léxica: {metadata['lexical_diversity']:.2%}")

        # Análisis de sentimiento específico
        sentiment = metadata["sentiment_analysis"]
        print(f"\n😊 ANÁLISIS DE SENTIMIENTO (ESPAÑOL):")
        print(f"   • Publicaciones positivas: {sentiment['positive']}")
        print(f"   • Publicaciones negativas: {sentiment['negative']}")
        print(f"   • Publicaciones neutrales: {sentiment['neutral']}")
        print(f"   • Polaridad promedio: {sentiment['avg_polarity']:.3f}")

        # Guardar resultados
        analyzer.save_results("big5_analisis_español")

        # Estadísticas finales
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"⏱️  TIEMPO TOTAL: {format_duration(total_time)}")
        print(f"📈 Posts/minuto: {len(posts) / (total_time/60):.1f}")
        print("=" * 60)
        print("✅ Análisis de personalidad en español completado exitosamente!")

    except KeyboardInterrupt:
        print("\n🛑 Proceso cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante el análisis en español: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
