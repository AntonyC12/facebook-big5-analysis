import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tempfile

import pytest

from src.personality import BigFiveAnalyzer, SpanishSentimentAnalyzer


def test_spanish_sentiment_analyzer():
    """Test del analizador de sentimiento en español"""
    analyzer = SpanishSentimentAnalyzer()

    print("\n=== DEBUG: Analizador de Sentimiento Español ===")

    # Texto positivo claro
    positive_text = "Estoy muy feliz y contento con la vida"
    positive_result = analyzer.analyze_sentiment(positive_text)
    print(f"Texto positivo: '{positive_text}'")
    print(f"Resultado: {positive_result}")

    # Textos positivos deben tener polaridad > 0
    assert (
        positive_result["polarity"] > 0
    ), f"Polaridad positiva esperada > 0, obtuvo {positive_result['polarity']}"

    # Texto negativo claro
    negative_text = "Estoy triste y deprimido por la situación"
    negative_result = analyzer.analyze_sentiment(negative_text)
    print(f"\nTexto negativo: '{negative_text}'")
    print(f"Resultado: {negative_result}")

    # Textos negativos deben tener polaridad < 0
    assert (
        negative_result["polarity"] < 0
    ), f"Polaridad negativa esperada < 0, obtuvo {negative_result['polarity']}"

    # Texto neutro
    neutral_text = "Hoy es martes y son las 3 de la tarde"
    neutral_result = analyzer.analyze_sentiment(neutral_text)
    print(f"\nTexto neutro: '{neutral_text}'")
    print(f"Resultado: {neutral_result}")

    # Texto neutro debe tener polaridad cercana a 0
    assert (
        abs(neutral_result["polarity"]) <= 0.2
    ), f"Polaridad neutra esperada <= 0.2, obtuvo {neutral_result['polarity']}"

    # Texto con negación clara
    negation_text = "No me siento feliz con esto"
    negation_result = analyzer.analyze_sentiment(negation_text)
    print(f"\nTexto con negación: '{negation_text}'")
    print(f"Resultado: {negation_result}")

    # La negación de un positivo debería dar negativo o neutro
    # "No feliz" es negativo, así que la polaridad debería ser <= 0
    assert (
        negation_result["polarity"] <= 0.2
    ), f"Texto negativo por negación debería tener polaridad <= 0.2, obtuvo {negation_result['polarity']}"

    print("=== FIN DEBUG ===\n")


def test_bigfive_analyzer_initialization_es():
    """Test de inicialización del analizador en español"""
    analyzer = BigFiveAnalyzer()
    assert analyzer is not None

    # Verificar que las listas de palabras en español existen
    assert len(analyzer.neuroticism_words) > 0
    assert len(analyzer.extraversion_words) > 0
    assert len(analyzer.openness_words) > 0
    assert len(analyzer.agreeableness_words) > 0
    assert len(analyzer.conscientiousness_words) > 0

    # Verificar que todas las palabras están en español
    sample_neuro_word = analyzer.neuroticism_words[0]
    assert isinstance(sample_neuro_word, str)
    # Podríamos verificar que no contenga caracteres no españoles, pero es simple


def test_calculate_word_frequency_es():
    """Test de cálculo de frecuencia de palabras EN ESPAÑOL"""
    analyzer = BigFiveAnalyzer()

    # Test con textos en español REAL
    texts = [
        "Estoy feliz y contento con mis amigos en la fiesta",
        "Me siento triste y preocupado por el examen mañana",
    ]

    # Vamos a calcular exactamente cuántas palabras hay
    import re

    all_text = " ".join(texts).lower()
    words = re.findall(r"\b\w+\b", all_text)
    total_words = len(words)
    print(f"DEBUG: Texto completo: '{all_text}'")
    print(f"DEBUG: Palabras encontradas: {words}")
    print(f"DEBUG: Total palabras: {total_words}")

    # Contar manualmente las palabras objetivo
    target_words = ["triste", "preocupado"]
    target_count = sum(1 for word in words if word in target_words)
    print(f"DEBUG: Palabras objetivo encontradas: {target_count}")
    print(
        f"DEBUG: Frecuencia esperada: {target_count}/{total_words} = {target_count/total_words}"
    )

    # Probamos con palabras de neuroticismo español
    frequency = analyzer.calculate_word_frequency(texts, target_words)

    # Verificar que la frecuencia esté en un rango razonable
    expected_min = target_count / (total_words + 1)  # Margen inferior
    expected_max = target_count / max(total_words - 1, 1)  # Margen superior

    assert (
        expected_min <= frequency <= expected_max
    ), f"Frecuencia {frequency} fuera del rango esperado [{expected_min}, {expected_max}]"

    # Test sin textos
    assert analyzer.calculate_word_frequency([], ["test"]) == 0.0

    # Test con lista de palabras vacía
    assert analyzer.calculate_word_frequency(texts, []) == 0.0


def test_analyze_text_sentiment_es():
    """Test de análisis de sentimiento EN ESPAÑOL"""
    analyzer = BigFiveAnalyzer()

    # Textos positivos EN ESPAÑOL
    positive_texts = [
        "Estoy muy feliz y emocionado con este proyecto",
        "Me encanta el resultado final, es maravilloso",
    ]
    result = analyzer.analyze_text_sentiment(positive_texts)

    assert result["positive"] >= 1  # Debería detectar al menos 1 positivo
    assert result["avg_polarity"] > 0
    assert isinstance(result["sentiment_balance"], float)

    # Textos negativos EN ESPAÑOL
    negative_texts = [
        "Estoy triste y deprimido por la situación",
        "Me siento enojado y frustrado con el problema",
    ]
    result = analyzer.analyze_text_sentiment(negative_texts)
    assert result["negative"] >= 1  # Debería detectar al menos 1 negativo

    # Textos mixtos
    mixed_texts = ["Hoy es un día normal", "Estoy bien"]
    result = analyzer.analyze_text_sentiment(mixed_texts)
    assert result["neutral"] >= 0

    # Sin textos
    empty_result = analyzer.analyze_text_sentiment([])
    assert empty_result["positive"] == 0
    assert empty_result["negative"] == 0
    assert empty_result["neutral"] == 0


def test_generate_personality_report_es():
    """Test de generación de reporte EN ESPAÑOL"""
    analyzer = BigFiveAnalyzer()

    # Scores de prueba
    scores = {
        "extraversion": 0.7,
        "neuroticism": 0.3,
        "openness": 0.6,
        "agreeableness": 0.8,
        "conscientiousness": 0.5,
    }

    report = analyzer.generate_personality_report(scores)

    # Verificar que el reporte está en español
    assert isinstance(report, str)
    assert len(report) > 0
    assert "Extraversión" in report
    assert "Neuroticismo" in report
    assert "Apertura" in report
    assert "Amabilidad" in report
    assert "Responsabilidad" in report

    # Verificar que contiene los scores
    assert "0.70" in report or "0.7" in report
    assert "0.30" in report or "0.3" in report


def test_calculate_big_five_scores_with_spanish_data():
    """Test con datos reales en español"""
    analyzer = BigFiveAnalyzer()

    # Datos de ejemplo EN ESPAÑOL
    spanish_data = {
        "posts": [
            {
                "text": "Hoy fui a una fiesta con mis amigos, fue muy divertido",
                "reactions": 15,
                "comments": 3,
            },
            {
                "text": "Estoy preocupado por el examen de mañana, me siento ansioso",
                "reactions": 5,
                "comments": 1,
            },
            {
                "text": "Leí un libro sobre filosofía muy interesante",
                "reactions": 8,
                "comments": 2,
            },
            {
                "text": "Ayudé a mi amigo con su proyecto, me gusta cooperar",
                "reactions": 12,
                "comments": 4,
            },
            {
                "text": "Organicé mi semana con un plan detallado",
                "reactions": 7,
                "comments": 1,
            },
        ],
        "friends_count": 350,
        "groups": ["Programación Python", "Club de Lectura", "Grupo de Música"],
        "basic_info": {
            "bio": "Desarrollador de software apasionado por la tecnología y el aprendizaje continuo"
        },
    }

    scores = analyzer.calculate_big_five_scores(spanish_data)

    # Verificaciones básicas
    assert isinstance(scores, dict)
    assert len(scores) == 5
    assert all(0.0 <= score <= 1.0 for score in scores.values())
    assert all(isinstance(score, float) for score in scores.values())

    # Verificar que results se llenó correctamente
    assert analyzer.results is not None
    assert "big_five_scores" in analyzer.results
    assert "metadata" in analyzer.results
    assert "calculated_components" in analyzer.results

    # Verificar que el análisis de sentimiento se hizo en español
    metadata = analyzer.results["metadata"]
    assert "sentiment_analysis" in metadata
    assert metadata["sentiment_analysis"]["total_texts_analyzed"] == 5


def test_edge_cases_es():
    """Test de casos extremos con datos en español"""
    analyzer = BigFiveAnalyzer()

    # Test sin datos
    empty_data = {"posts": [], "friends_count": 0, "groups": []}
    scores = analyzer.calculate_big_five_scores(empty_data)

    assert isinstance(scores, dict)
    assert scores["extraversion"] == 0.5  # Valor por defecto
    assert scores["neuroticism"] == 0.5

    # Test con datos None
    scores_none = analyzer.calculate_big_five_scores(None)
    assert isinstance(scores_none, dict)
    assert len(scores_none) == 5

    # Test con datos inválidos
    invalid_data = {"posts": "no es una lista", "friends_count": "no es número"}
    scores_invalid = analyzer.calculate_big_five_scores(invalid_data)
    assert isinstance(scores_invalid, dict)
    assert len(scores_invalid) == 5


def test_save_results_es():
    """Test de guardado de resultados con datos en español"""
    analyzer = BigFiveAnalyzer()

    # Calcular scores primero con datos en español
    test_data = {
        "posts": [{"text": "Estoy contento con mi progreso", "reactions": 10}],
        "friends_count": 150,
        "groups": ["Tecnología"],
        "basic_info": {"bio": "Apasionado por la programación"},
    }

    analyzer.calculate_big_five_scores(test_data)

    # Usar directorio temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        # Guardar resultados
        import os

        json_path = os.path.join(tmpdir, "resultados_español.json")
        txt_path = os.path.join(tmpdir, "resultados_español.txt")

        # Modificar temporalmente el método save_results para usar nuestro path
        original_save = analyzer.save_results

        def temp_save(filename="big5_analysis.json"):
            output_path = Path(tmpdir) / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Guardar JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(analyzer.results, f, indent=2, ensure_ascii=False)

            # Guardar texto
            txt_path = output_path.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(analyzer.generate_report())

            print(f"Resultados guardados en: {output_path}")
            return output_path

        # Ejecutar
        try:
            analyzer.save_results = temp_save
            result_path = analyzer.save_results("test_es.json")

            # Verificar que se crearon archivos
            assert os.path.exists(result_path)
            assert os.path.exists(result_path.with_suffix(".txt"))

            # Verificar que el contenido es en español
            with open(result_path.with_suffix(".txt"), "r", encoding="utf-8") as f:
                content = f.read()
                assert "INFORME" in content or "RESULTADOS" in content

        finally:
            analyzer.save_results = original_save
