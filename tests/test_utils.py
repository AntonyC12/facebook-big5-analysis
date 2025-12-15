# tests/test_utils.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from pathlib import Path

import pytest

from src.utils import format_duration, load_json, save_json


def test_save_and_load_json(tmp_path):
    """Test de guardado y carga de JSON"""
    # Usar directorio temporal
    test_data = {"test": "value", "number": 42, "list": [1, 2, 3]}

    # Guardar
    saved_path = save_json(test_data, "test_file", folder=str(tmp_path))
    assert saved_path.exists()

    # Cargar
    loaded_data = load_json(saved_path.name, folder=str(tmp_path))
    assert loaded_data == test_data


def test_format_duration():
    """Test de formato de duración"""
    assert format_duration(30) == "30.0 segundos"
    assert format_duration(90) == "1.5 minutos"
    assert format_duration(3600) == "1.0 horas"
    assert format_duration(7200) == "2.0 horas"


def test_save_json_with_timestamp(tmp_path):
    """Test de guardado con timestamp automático"""
    test_data = {"test": "data"}

    # Sin extensión debería añadir timestamp
    saved_path = save_json(test_data, "test", folder=str(tmp_path))
    assert saved_path.suffix == ".json"
    assert "_" in saved_path.stem  # Contiene timestamp

    # Con extensión .json
    saved_path2 = save_json(test_data, "test2.json", folder=str(tmp_path))
    assert saved_path2.suffix == ".json"
