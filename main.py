import time
import sys
from src.scraper import FacebookScraper
from src.personality import BigFiveAnalyzer
from src.utils import save_json, format_duration
from config import TARGET_PROFILE_URL, MAX_POSTS, HEADLESS_BROWSER

def main():
    print("🚀 INICIANDO ANÁLISIS DE PERSONALIDAD FACEBOOK")
    print("="*60)
    print(f"📁 Perfil objetivo: {TARGET_PROFILE_URL}")
    print(f"📊 Máximo de posts: {MAX_POSTS}")
    print(f"👁️  Modo headless: {HEADLESS_BROWSER}")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # 1. SCRAPING
        print("\n🔍 Fase 1: Scraping de datos...")
        with FacebookScraper(headless=HEADLESS_BROWSER) as scraper:
            # Asegurar login
            scraper.ensure_login()
            
            # Navegar al perfil
            scraper.navigate_to_profile(TARGET_PROFILE_URL)
            
            # Extraer datos
            print("   📋 Extrayendo información básica...")
            basic_info = scraper.extract_basic_info()
            print(f"      ✓ Nombre: {basic_info.get('name', 'No encontrado')}")
            
            print(f"   📄 Extrayendo hasta {MAX_POSTS} publicaciones...")
            posts = scraper.extract_posts(max_posts=MAX_POSTS)
            print(f"      ✓ {len(posts)} publicaciones obtenidas")
            
            print("   👥 Extrayendo amigos...")
            friends_count = scraper.extract_friends_count()
            print(f"      ✓ {friends_count} amigos detectados")
            
            print("   👥 Extrayendo grupos...")
            groups = scraper.extract_groups()
            print(f"      ✓ {len(groups)} grupos encontrados")
            
            # Compilar datos
            sample_data = {
                "basic_info": basic_info,
                "posts": posts,
                "friends_count": friends_count,
                "groups": groups,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Guardar datos crudos
        raw_file = save_json(sample_data, "facebook_data")
        print(f"✅ Scraping completado - Datos en: {raw_file}")
        
        # 2. ANÁLISIS
        print("\n🧠 Fase 2: Análisis de personalidad...")
        analyzer = BigFiveAnalyzer()
        
        # Calcular puntuaciones
        scores = analyzer.calculate_big_five_scores(sample_data)
        
        # Generar reporte
        report = analyzer.generate_personality_report(scores)
        
        print("\n" + "="*60)
        print("📊 RESULTADOS BIG FIVE:")
        print("="*60)
        print(report)
        print("="*60)
        
        # Guardar resultados
        analyzer.save_results("big5_analysis")
        
        # 3. ESTADÍSTICAS
        duration = time.time() - start_time
        print(f"\n⏱️  Duración total: {format_duration(duration)}")
        print(f"📊 Publicaciones analizadas: {analyzer.results['metadata']['posts_analyzed']}")
        print(f"🔤 Palabras analizadas: {analyzer.results['metadata']['words_analyzed']:,}")
        print(f"💾 Resultados guardados en: data/results/")
        print("\n🎉 Análisis completado exitosamente!")
        
        # Mostrar ubicación archivos
        print("\n📁 ARCHIVOS GENERADOS:")
        print(f"   • Datos crudos: data/raw_json/facebook_data_*.json")
        print(f"   • Resultados JSON: data/results/big5_analysis_*.json")
        print(f"   • Reporte texto: data/results/big5_analysis_*.txt")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Proceso cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()