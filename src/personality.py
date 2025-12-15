# src/personality.py
import re
from collections import Counter
from typing import Dict, List, Tuple
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
        """Calcula puntuaciones para los cinco rasgos."""
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