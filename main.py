# main.py
import time
from src.scraper import FacebookScraper
from src.personality import BigFiveAnalyzer
from src.utils import save_json, format_duration
from config import RAW_DATA_PATH

def main():
    print("🚀 INICIANDO ANÁLISIS DE PERSONALIDAD FACEBOOK")
    print("="*60)
    
    # URL del perfil objetivo (MODIFICA ESTA URL)
    profile_url = "https://facebook.com/tu_perfil_o_amigo"
    
    start_time = time.time()
    
    try:
        # 1. SCRAPING
        print("🔍 Fase 1: Scraping de datos...")
        with FacebookScraper(headless=False) as scraper:
            # Asegurar login (manual la primera vez)
            scraper.ensure_login()
            
            # Extraer datos básicos
            basic_info = scraper.scrape_profile_basic_info(profile_url)
            print(f"   📋 Info básica obtenida: {basic_info.get('name', 'No encontrado')}")
            
            # Extraer posts
            posts = scraper.scrape_posts(max_posts=30)
            print(f"   📄 {len(posts)} publicaciones obtenidas")
            
            # Simular amigos y grupos (por ahora datos de ejemplo)
            # En un scraper real, implementarías scrape_friends() y scrape_groups()
            sample_data = {
                "basic_info": basic_info,
                "posts": posts,
                "friends_count": 500,  # Ejemplo
                "groups": ["Programación", "Música", "Deportes"],  # Ejemplo
            }
        
        # Guardar datos crudos
        save_json(sample_data, "facebook_data")
        print("✅ Scraping completado")
        
        # 2. ANÁLISIS
        print("\n🧠 Fase 2: Análisis de personalidad...")
        analyzer = BigFiveAnalyzer()
        
        # Calcular puntuaciones Big Five
        scores = analyzer.calculate_big_five_scores(sample_data)
        
        # Generar reporte
        report = analyzer.generate_personality_report(scores)
        
        print("\n" + "="*60)
        print("📊 RESULTADOS BIG FIVE:")
        print("="*60)
        print(report)
        print("="*60)
        
        # Guardar resultados
        save_json(analyzer.results, "big5_results", folder="results")
        
        # 3. ESTADÍSTICAS
        duration = time.time() - start_time
        print(f"\n⏱️  Duración total: {format_duration(duration)}")
        print(f"📊 Publicaciones analizadas: {analyzer.results['metadata']['posts_analyzed']}")
        print(f"🔤 Palabras analizadas: {analyzer.results['metadata']['words_analyzed']:,}")
        print("\n🎉 Análisis completado exitosamente!")
        
    except KeyboardInterrupt:
        print("\n🛑 Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        raise

if __name__ == "__main__":
    main()