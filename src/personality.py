# src/personality.py
import re
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List
from textblob import TextBlob

class BigFiveAnalyzer:
    def __init__(self):
        # Palabras clave para cada rasgo (pueden extenderse)
        self.neuroticism_words = [
            'ansioso', 'preocupado', 'nervioso', 'triste', 'enfadado',
            'estresado', 'miedo', 'pánico', 'desesperado', 'culpable'
        ]

        self.extraversion_words = [
            'fiesta', 'amigos', 'social', 'divertido', 'energía',
            'hablar', 'grupo', 'celebración', 'reunión', 'alegre'
        ]

        self.openness_words = [
            'arte', 'música', 'creativo', 'innovador', 'imaginación',
            'curioso', 'aprender', 'filosofía', 'viajar', 'cultura'
        ]

        self.agreeableness_words = [
            'amable', 'compasivo', 'ayudar', 'cooperar', 'empatía',
            'perdonar', 'generoso', 'considerado', 'paciente', 'apoyar'
        ]

        self.conscientiousness_words = [
            'organizado', 'responsable', 'disciplinado', 'trabajo', 'esfuerzo',
            'planificar', 'cumplir', 'puntual', 'detallista', 'persistente'
        ]

        # Atributo para almacenar resultados
        self.results = {}

    def analyze_text_sentiment(self, texts: List[str]) -> Dict:
        """Analiza el sentimiento de una lista de textos."""
        positive = 0
        negative = 0
        neutral = 0
        polarities = []

        for text in texts:
            if not text or len(text.strip()) < 10:
                continue

            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            polarities.append(polarity)

            if polarity > 0.1:
                positive += 1
            elif polarity < -0.1:
                negative += 1
            else:
                neutral += 1

        total = len(polarities) if polarities else 1
        avg_polarity = sum(polarities) / total if polarities else 0

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "avg_polarity": avg_polarity,
            "sentiment_balance": positive / total if total > 0 else 0
        }

    def calculate_word_frequency(self, texts: List[str], word_list: List[str]) -> float:
        """Calcula la frecuencia de palabras de una lista en los textos."""
        if not texts:
            return 0

        all_text = ' '.join(texts).lower()
        words = re.findall(r'\b\w+\b', all_text)
        total_words = len(words)

        if total_words == 0:
            return 0

        target_count = sum(1 for word in words if word in word_list)
        return target_count / total_words

    def calculate_big_five_scores(self, data: Dict) -> Dict[str, float]:
        """Calcula puntuaciones para los cinco rasgos y almacena en self.results."""
        if not data or not data.get("posts"):
            return {"error": "No hay datos para analizar"}
        
        posts_text = [post.get("text", "") for post in data.get("posts", [])]
        all_text = ' '.join(posts_text)

        # Extraversión: basada en interacciones sociales
        extraversion_score = (
            data.get("friends_count", 0) / 1000 +  # Normalizar amigos
            sum(post.get("reactions", 0) for post in data.get("posts", [])) / max(len(posts_text), 1) / 10 +
            self.calculate_word_frequency(posts_text, self.extraversion_words)
        ) / 3

        # Neuroticismo: basado en sentimiento negativo
        sentiment = self.analyze_text_sentiment(posts_text)
        neuroticism_score = (
            sentiment["negative"] / max(len(posts_text), 1) +
            (1 - sentiment["sentiment_balance"]) / 2 +
            self.calculate_word_frequency(posts_text, self.neuroticism_words)
        ) / 3

        # Apertura: basada en diversidad de intereses
        openness_score = (
            len(data.get("groups", [])) / 20 +  # Normalizar grupos
            self.calculate_word_frequency(posts_text, self.openness_words) +
            len(set(re.findall(r'\b\w+\b', all_text))) / max(len(re.findall(r'\b\w+\b', all_text)), 1)  # Riqueza léxica
        ) / 3

        # Amabilidad: basada en lenguaje positivo y cooperativo
        agreeableness_score = (
            sentiment["positive"] / max(len(posts_text), 1) +
            self.calculate_word_frequency(posts_text, self.agreeableness_words) +
            (sum(post.get("comments", 0) for post in data.get("posts", [])) / max(len(posts_text), 1) / 5)
        ) / 3

        # Responsabilidad: basada en regularidad y lenguaje organizado
        conscientiousness_score = (
            self.calculate_word_frequency(posts_text, self.conscientiousness_words) +
            (1 if len(posts_text) > 10 else 0.5) +  # Consistencia en publicar
            (1 if data.get("basic_info", {}).get("bio", "") else 0.5)  # Tener biografía completa
        ) / 3

        # Normalizar scores a 0-1
        scores = {
            "extraversion": min(max(extraversion_score, 0), 1),
            "neuroticism": min(max(neuroticism_score, 0), 1),
            "openness": min(max(openness_score, 0), 1),
            "agreeableness": min(max(agreeableness_score, 0), 1),
            "conscientiousness": min(max(conscientiousness_score, 0), 1)
        }

        # Almacenar resultados en self.results
        self.results = {
            "big_five_scores": scores,
            "metadata": {
                "posts_analyzed": len(posts_text),
                "words_analyzed": len(re.findall(r'\b\w+\b', all_text)),
                "unique_words": len(set(re.findall(r'\b\w+\b', all_text))),
                "sentiment_analysis": sentiment
            }
        }

        return scores

    def generate_personality_report(self, scores: Dict[str, float]) -> str:
        """Genera un reporte descriptivo basado en los scores."""
        report = []

        for trait, score in scores.items():
            if score < 0.3:
                level = "Muy bajo"
            elif score < 0.45:
                level = "Bajo"
            elif score < 0.55:
                level = "Promedio"
            elif score < 0.7:
                level = "Alto"
            else:
                level = "Muy alto"

            # Descripciones para cada rasgo
            descriptions = {
                "extraversion": f"Extraversión ({score:.2f}): {level}. ",
                "neuroticism": f"Neuroticismo ({score:.2f}): {level}. ",
                "openness": f"Apertura a la experiencia ({score:.2f}): {level}. ",
                "agreeableness": f"Amabilidad ({score:.2f}): {level}. ",
                "conscientiousness": f"Responsabilidad ({score:.2f}): {level}. "
            }

            report.append(descriptions[trait])

        return "\n".join(report)

    def generate_report(self) -> str:
        """Genera un reporte legible de los resultados almacenados en self.results."""
        if not self.results:
            return "No hay resultados para reportar"

        scores = self.results.get("big_five_scores", {})
        metadata = self.results.get("metadata", {})

        report = []
        report.append("="*60)
        report.append("📊 INFORME DE ANÁLISIS DE PERSONALIDAD (BIG FIVE)")
        report.append("="*60)
        report.append("")

        # Metadatos
        report.append(f"📈 METADATOS DEL ANÁLISIS:")
        report.append(f"   • Publicaciones analizadas: {metadata.get('posts_analyzed', 0)}")
        report.append(f"   • Palabras analizadas: {metadata.get('words_analyzed', 0):,}")
        report.append(f"   • Palabras únicas: {metadata.get('unique_words', 0):,}")
        report.append("")

        # Puntuaciones Big Five
        report.append("🎭 PUNTUACIONES BIG FIVE (0-1):")

        # Mapeo de rasgos a descripciones
        trait_descriptions = {
            "neuroticism": ("Neuroticismo", "Inestabilidad emocional vs. estabilidad"),
            "extraversion": ("Extraversión", "Sociabilidad vs. introversión"),
            "openness": ("Apertura", "Creatividad vs. convencionalidad"),
            "agreeableness": ("Amabilidad", "Cooperación vs. competitividad"),
            "conscientiousness": ("Responsabilidad", "Organización vs. espontaneidad")
        }

        for trait_key, (trait_name, description) in trait_descriptions.items():
            score = scores.get(trait_key, 0)
            # Convertir a escala 0-100 para la barra
            score_percent = score * 100
            bar_length = int(score_percent / 5)  # 5% por carácter
            bar = "█" * bar_length + "░" * (20 - bar_length)

            # Interpretación
            if score < 0.3:
                interpretation = "BAJO"
            elif score < 0.5:
                interpretation = "MEDIO-BAJO"
            elif score < 0.7:
                interpretation = "MEDIO-ALTO"
            else:
                interpretation = "ALTO"

            report.append(f"   {trait_name.upper():20} {score:.2f} {bar} ({interpretation})")
            report.append(f"     ↳ {description}")

        report.append("")
        report.append("📋 INTERPRETACIÓN:")
        report.append("")

        # Análisis de sentimiento
        sentiment = metadata.get('sentiment_analysis', {})
        if sentiment:
            report.append(f"1. SENTIMIENTO GENERAL:")
            report.append(f"   Publicaciones positivas: {sentiment.get('positive', 0)}")
            report.append(f"   Publicaciones negativas: {sentiment.get('negative', 0)}")
            report.append(f"   Publicaciones neutrales: {sentiment.get('neutral', 0)}")
            report.append(f"   Polaridad promedio: {sentiment.get('avg_polarity', 0):.3f}")
            report.append("")

        report.append("="*60)
        report.append("⚠️  NOTA: Este análisis es aproximado y con fines académicos.")
        report.append("    Para evaluación psicológica profesional, consulte a un especialista.")
        report.append("="*60)

        return "\n".join(report)

    def save_results(self, filename: str = "big5_analysis.json"):
        """Guarda los resultados en un archivo JSON y el reporte en texto."""
        if not self.results:
            print("No hay resultados para guardar. Ejecute calculate_big_five_scores primero.")
            return

        output_path = Path("data/results") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"💾 Resultados guardados en: {output_path}")

        # Guardar también reporte en texto
        txt_path = output_path.with_suffix('.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())

        print(f"📄 Reporte guardado en: {txt_path}")