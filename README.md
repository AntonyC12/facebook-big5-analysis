# Facebook Big Five Personality Analysis

Proyecto académico para análisis de personalidad Big Five (OCEAN) mediante scraping de Facebook.

## ⚠️ Advertencia importante

Este proyecto es **estrictamente académico**. El scraping de Facebook viola sus Términos de Servicio. Úsalo solo con tus propias cuentas y bajo tu propio riesgo. Las cuentas pueden ser bloqueadas por Facebook.

## Características

- ✅ Scraping de Facebook con manejo de cookies para sesiones persistentes
- ✅ Extracción de publicaciones, amigos, grupos e información básica
- ✅ Análisis de personalidad según el modelo Big Five (OCEAN)
- ✅ Generación de reportes detallados en JSON y texto
- ✅ Configuración mediante variables de entorno
- ✅ Manejo de errores y tiempos de espera aleatorios

## Estructura del proyecto

```text
facebook-big5-analysis/
├── src/ # Código fuente
│ ├── scraper.py # Scraping de Facebook con Playwright
│ ├── personality.py # Analizador Big Five
│ └── utils.py # Funciones auxiliares
├── data/ # Datos y resultados
│ ├── cookies/ # Cookies de sesión (no se sube a git)
│ ├── raw_json/ # Datos crudos scrapeados
│ └── results/ # Resultados del análisis
├── tests/ # Pruebas unitarias
├── .env.example # Plantilla de variables de entorno
├── config.py # Configuración
├── main.py # Punto de entrada
├── requirements.txt # Dependencias
├── LICENSE # Licencia MIT
└── README.md # Este archivo
```

## Instalación
1. Clonar repositorio: git `clone https://github.com/AntonioC12/facebook-big5-analysis.git` & `cd facebook-big5-analysis`
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `.\venv\Scripts\activate` (Windows) || `source venv/bin/activate` (Linux/Mac)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Instalar Playwright: `playwright install chromium`
6. Configurar variables de entorno: `cp .env.example .env`

## Configuración
Edita el archivo .env con tus datos:
# URL del perfil objetivo (debe ser amigo de la cuenta de scraping)
TARGET_PROFILE_URL=https://facebook.com/tu_perfil_principal
# Configuración de scraping
MAX_POSTS=50
HEADLESS_BROWSER=False

## Uso
1. Ejecutar el análisis: `python main.py`
2. La primera vez, hacer login manual en la ventana del navegador.
3. Después del login, las cookies se guardarán automáticamente para sesiones futuras.
4. El scraper navegará al perfil objetivo y extraerá:
* Información básica (nombre, biografía)
* Publicaciones (texto, reacciones, comentarios)
* Número de amigos
* Lista de grupos
5. Los datos se analizarán y se generará un reporte de personalidad Big Five.
6. Los resultados se guardan en:
`data/results/big5_results_<timestamp>.json (datos completos)`
`data/results/big5_results_<timestamp>.txt (reporte legible)`

## Modelo Big Five (OCEAN)
El análisis evalúa cinco dimensiones de personalidad:
1. Extraversión: Sociabilidad, energía, asertividad
2. Amabilidad: Cooperación, empatía, compasión
3. Responsabilidad: Organización, disciplina, confiabilidad
4. Neuroticismo: Inestabilidad emocional, ansiedad
5. Apertura a la experiencia: Creatividad, curiosidad, imaginación

## Limitaciones y consideraciones
* Los selectores de Facebook pueden cambiar, rompiendo el scraping.
* El análisis de personalidad es aproximado y no sustituye una evaluación profesional.
* Facebook puede detectar y bloquear cuentas por scraping.
* Solo funciona con perfiles públicos o accesibles para la cuenta de scraping.

## Soluciones a Problemas
* "No se encuentran elementos en la página"
Los selectores de Facebook pueden haber cambiado. Inspecciona la página y actualiza los selectores en "scraper.py".

* "Error de timeout"
Facebook puede estar cargando contenido dinámico. Aumenta los tiempos de espera en config.py.

* "Cuenta bloqueada"
Facebook ha detectado scraping. Deja de usar el script y revisa la política de Facebook.

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Licencia
Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## Notas importantes
- **Solo para uso académico**
- Usar únicamente con cuentas propias
- Facebook puede bloquear cuentas por scraping
- Modificar `TARGET_PROFILE` en `main.py` antes de ejecutar

