# src/__init__.py
"""
Paquete principal del proyecto Facebook Big Five Analysis.

Este archivo __init__.py hace que Python trate el directorio 'src'
como un paquete, permitiendo:
1. Importar módulos de forma limpia: from src.scraper import FacebookScraper
2. Definir variables/constantes a nivel de paquete
3. Ejecutar código de inicialización del paquete
"""

__version__ = "1.0.0"
__author__ = "Antony Coello"
__email__ = "coelloantony1212@gmail.com"

from .personality import BigFiveAnalyzer
# Exponer las clases principales para importación fácil
from .scraper import FacebookScraper
from .utils import format_duration, load_json, save_json

# Lista de lo que se exporta por defecto
__all__ = [
    "FacebookScraper",
    "BigFiveAnalyzer",
    "save_json",
    "load_json",
    "format_duration",
]
