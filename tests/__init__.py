# tests/__init__.py
"""
Paquete de tests unitarios para Facebook Big Five Analysis.

Este archivo __init__.py hace que Python trate el directorio 'tests' 
como un paquete, permitiendo:
1. Ejecutar tests con pytest
2. Importar módulos de tests
3. Configurar fixtures globales
"""

# Configuración global para tests
import sys
from pathlib import Path

# Añadir el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))