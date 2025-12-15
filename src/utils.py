# src/utils.py
import json
from pathlib import Path
from typing import Any, Dict

def save_json(data: Dict[str, Any], filepath: Path):
    """Guarda datos en formato JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: Path) -> Dict[str, Any]:
    """Carga datos desde un archivo JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_data_structure(data: Dict) -> bool:
    """Valida la estructura básica de los datos scrapeados."""
    required_keys = ['posts', 'basic_info']
    return all(key in data for key in required_keys)