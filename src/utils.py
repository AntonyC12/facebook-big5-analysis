# src/utils.py
import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

def save_json(data: Any, filename: str, folder: str = "raw_json") -> Path:
    """Guarda datos como JSON en la carpeta especificada"""
    output_dir = Path("data") / folder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Añadir timestamp si no tiene extensión
    if not filename.endswith('.json'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}.json"
    elif not filename.endswith('.json'):
        filename += ".json"
    
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Datos guardados en: {filepath}")
    return filepath

def load_json(filename: str, folder: str = "raw_json") -> Dict:
    """Carga datos desde un archivo JSON"""
    filepath = Path("data") / folder / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_duration(seconds: float) -> str:
    """Formatea segundos a un string legible"""
    if seconds < 60:
        return f"{seconds:.1f} segundos"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutos"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} horas"