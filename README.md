# facebook-big5-analysis
Proyecto académico para análisis de personalidad Big Five mediante scraping de Facebook

# Facebook Big Five Personality Analysis

Proyecto académico para análisis de personalidad Big Five mediante scraping de Facebook.

## Características
- Scraping de Facebook con manejo de cookies para sesiones persistentes
- Extracción de publicaciones, amigos, grupos e información básica
- Análisis de personalidad según el modelo Big Five (OCEAN)
- Generación de reportes detallados en JSON y texto

## Estructura del Proyecto
facebook-big5-analysis/
├── src/ # Código fuente
│ ├── scraper.py # Scraper de Facebook
│ ├── personality.py # Analizador Big Five
│ └── utils.py # Funciones auxiliares
├── data/ # Datos y resultados
│ ├── cookies/ # Cookies de sesión
│ ├── raw_json/ # Datos scrapeados
│ └── results/ # Resultados del análisis
├── tests/ # Pruebas unitarias
├── main.py # Punto de entrada
└── requirements.txt # Dependencias

## Instalación
1. Clonar repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `.\venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Instalar Playwright: `playwright install chromium`

## Uso
1. Ejecutar: `python main.py`
2. La primera vez, hacer login manual en la ventana del navegador
3. Las cookies se guardarán para sesiones futuras
4. Los resultados se guardan en `data/results/`

## Notas importantes
- **Solo para uso académico**
- Usar únicamente con cuentas propias
- Facebook puede bloquear cuentas por scraping
- Modificar `TARGET_PROFILE` en `main.py` antes de ejecutar