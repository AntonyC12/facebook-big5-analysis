# src/personality.py
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


class SpanishSentimentAnalyzer:
    """Analizador de sentimiento para español basado en diccionarios"""

    # Diccionarios de sentimiento en español (expandidos)
    POSITIVE_WORDS = {
        "feliz",
        "contento",
        "alegre",
        "emocionado",
        "encantado",
        "amor",
        "maravilloso",
        "fantástico",
        "excelente",
        "genial",
        "increíble",
        "perfecto",
        "bueno",
        "bonito",
        "hermoso",
        "divertido",
        "agradable",
        "positivo",
        "optimista",
        "satisfecho",
        "encanta",
        "gusta",
        "apasiona",
        "entusiasma",
        "admira",
    }

    NEGATIVE_WORDS = {
        "triste",
        "deprimido",
        "enojado",
        "enfadado",
        "molesto",
        "frustrado",
        "asustado",
        "preocupado",
        "ansioso",
        "nervioso",
        "estresado",
        "malo",
        "horrible",
        "terrible",
        "pésimo",
        "aburrido",
        "cansado",
        "agotado",
        "desanimado",
        "desesperado",
        "odio",
        "detesto",
        "molesta",
        "irrita",
        "desagrada",
    }

    # Intensificadores y negaciones
    INTENSIFIERS = {
        "muy",
        "mucho",
        "realmente",
        "totalmente",
        "absolutamente",
        "extremadamente",
    }
    NEGATIONS = {"no", "nunca", "jamás", "tampoco", "nada", "ningún", "ninguna"}

    @classmethod
    def analyze_sentiment(cls, text: str) -> Dict[str, float]:
        """Analiza el sentimiento de un texto en español"""
        if not text or len(text.strip()) < 5:
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "label": "NEUTRO",
                "positive_score": 0,
                "negative_score": 0,
            }

        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "label": "NEUTRO",
                "positive_score": 0,
                "negative_score": 0,
            }

        positive_score = 0
        negative_score = 0
        total_words = len(words)

        i = 0
        while i < len(words):
            word = words[i]

            # Verificar negaciones (buscar en las siguientes 2 palabras)
            is_negated = False
            if word in cls.NEGATIONS:
                # Mirar las siguientes 1-3 palabras para ver si hay palabras de sentimiento
                for lookahead in range(1, min(4, len(words) - i)):
                    next_word = words[i + lookahead]
                    if next_word in cls.POSITIVE_WORDS:
                        negative_score += 1  # Negación de positivo = negativo
                        is_negated = True
                        i += lookahead  # Saltar palabras procesadas
                        break
                    elif next_word in cls.NEGATIVE_WORDS:
                        positive_score += 1  # Negación de negativo = positivo
                        is_negated = True
                        i += lookahead
                        break

            if is_negated:
                i += 1
                continue

            # Verificar intensificadores
            intensity = 1.0
            if word in cls.INTENSIFIERS and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word in cls.POSITIVE_WORDS or next_word in cls.NEGATIVE_WORDS:
                    intensity = 1.5

            # Contar palabras positivas/negativas
            if word in cls.POSITIVE_WORDS:
                positive_score += intensity
            elif word in cls.NEGATIVE_WORDS:
                negative_score += intensity

            i += 1

        # Calcular polaridad (-1 a 1)
        total_score = positive_score + negative_score
        if total_score > 0:
            polarity = (positive_score - negative_score) / total_score
        else:
            polarity = 0.0

        # Calcular subjetividad (0 a 1)
        subjectivity = total_score / total_words if total_words > 0 else 0.0

        # Etiquetar (umbrales más flexibles)
        if polarity > 0.15:
            label = "POSITIVO"
        elif polarity < -0.15:
            label = "NEGATIVO"
        else:
            label = "NEUTRO"

        return {
            "polarity": round(polarity, 3),
            "subjectivity": round(min(subjectivity, 1.0), 3),
            "label": label,
            "positive_score": positive_score,
            "negative_score": negative_score,
        }


class BigFiveAnalyzer:
    def __init__(self):
        # Palabras clave para cada rasgo EN ESPAÑOL (expandidas)
        self.neuroticism_words = [
            "ansioso",
            "preocupado",
            "nervioso",
            "triste",
            "enfadado",
            "estresado",
            "miedo",
            "pánico",
            "desesperado",
            "culpable",
            "deprimido",
            "angustiado",
            "inseguro",
            "temeroso",
            "asustado",
            "irritado",
            "frustrado",
            "abatido",
        ]

        self.extraversion_words = [
            "fiesta",
            "amigos",
            "social",
            "divertido",
            "energía",
            "hablar",
            "grupo",
            "celebración",
            "reunión",
            "alegre",
            "extrovertido",
            "risa",
            "baile",
            "concierto",
            "evento",
            "compañía",
            "socializar",
            "festejo",
            "júbilo",
        ]

        self.openness_words = [
            "arte",
            "música",
            "creativo",
            "innovador",
            "imaginación",
            "curioso",
            "aprender",
            "filosofía",
            "viajar",
            "cultura",
            "libro",
            "película",
            "nuevo",
            "diferente",
            "experiencia",
            "descubrir",
            "explorar",
            "conocimiento",
            "leer",
            "educación",
            "tecnología",
            "ciencia",
        ]

        self.agreeableness_words = [
            "amable",
            "compasivo",
            "ayudar",
            "cooperar",
            "empatía",
            "perdonar",
            "generoso",
            "considerado",
            "paciente",
            "apoyar",
            "amor",
            "cariño",
            "bondad",
            "respeto",
            "solidaridad",
            "comprender",
            "escuchar",
            "colaborar",
        ]

        self.conscientiousness_words = [
            "organizado",
            "responsable",
            "disciplinado",
            "trabajo",
            "esfuerzo",
            "planificar",
            "cumplir",
            "puntual",
            "detallista",
            "persistente",
            "metas",
            "logro",
            "estudio",
            "proyecto",
            "deadline",
            "eficiente",
            "productivo",
            "ordenado",
            "sistemático",
            "constante",
        ]

        # Inicializar resultados
        self.results = {}
        self.sentiment_analyzer = SpanishSentimentAnalyzer()

    def analyze_text_sentiment(self, texts: List[str]) -> Dict:
        """Analiza el sentimiento de una lista de textos EN ESPAÑOL"""
        positive = 0
        negative = 0
        neutral = 0
        polarities = []

        for text in texts:
            if not text or len(text.strip()) < 5:  # Reducido a 5 caracteres mínimo
                continue

            # Usar nuestro analizador en español
            sentiment = self.sentiment_analyzer.analyze_sentiment(text)
            polarities.append(sentiment["polarity"])

            if sentiment["polarity"] > 0.2:
                positive += 1
            elif sentiment["polarity"] < -0.2:
                negative += 1
            else:
                neutral += 1

        total = len(polarities) if polarities else 1
        avg_polarity = sum(polarities) / total if polarities else 0.0

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "avg_polarity": round(avg_polarity, 3),
            "sentiment_balance": positive / total if total > 0 else 0.0,
            "total_texts_analyzed": len(polarities),
        }

    def calculate_word_frequency(self, texts: List[str], word_list: List[str]) -> float:
        """Calcula la frecuencia de palabras de una lista en los textos."""
        if not texts or not word_list:
            return 0.0

        all_text = " ".join(texts).lower()
        words = re.findall(r"\b\w+\b", all_text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        # Contar palabras objetivo (insensible a mayúsculas/minúsculas)
        word_list_lower = [w.lower() for w in word_list]
        word_set = set(word_list_lower)

        target_count = sum(1 for word in words if word in word_set)

        return target_count / total_words

    def calculate_big_five_scores(self, data: Dict) -> Dict[str, float]:
        """Calcula puntuaciones para los cinco rasgos EN ESPAÑOL."""
        # Validación robusta
        if not data or not isinstance(data, dict):
            return self._get_default_scores()

        # Extraer posts de forma segura
        posts = data.get("posts", [])
        if not isinstance(posts, list):
            posts = []

        posts_text = []
        for post in posts:
            if isinstance(post, dict):
                text = post.get("text", "")
                if text and isinstance(text, str) and len(text.strip()) > 0:
                    posts_text.append(text.strip())

        # Si no hay textos válidos
        if not posts_text:
            return self._get_default_scores()

        all_text = " ".join(posts_text)

        # 1. EXTRAVERSIÓN
        friends_count = data.get("friends_count", 0)
        if not isinstance(friends_count, (int, float)):
            friends_count = 0

        # Calcular reacciones totales
        total_reactions = 0
        for post in posts:
            if isinstance(post, dict):
                reactions = post.get("reactions", 0)
                if isinstance(reactions, (int, float)):
                    total_reactions += reactions

        extraversion_score = (
            min(friends_count / 1000, 1.0) * 0.3  # Normalizar amigos (max 1000)
            + min(total_reactions / max(len(posts_text), 1) / 50, 1.0)
            * 0.4  # Reacciones por post
            + self.calculate_word_frequency(posts_text, self.extraversion_words) * 0.3
        )

        # 2. NEUROTICISMO
        sentiment = self.analyze_text_sentiment(posts_text)
        neuroticism_score = (
            (sentiment["negative"] / max(sentiment["total_texts_analyzed"], 1)) * 0.4
            + (1 - sentiment["sentiment_balance"]) * 0.3
            + self.calculate_word_frequency(posts_text, self.neuroticism_words) * 0.3
        )

        # 3. APERTURA
        groups = data.get("groups", [])
        if not isinstance(groups, list):
            groups = []

        # Calcular diversidad léxica
        words = re.findall(r"\b\w+\b", all_text)
        if words:
            unique_words = len(set(words))
            lexical_diversity = unique_words / len(words)
        else:
            lexical_diversity = 0

        openness_score = (
            min(len(groups) / 10, 1.0) * 0.3  # Normalizar grupos (max 10)
            + self.calculate_word_frequency(posts_text, self.openness_words) * 0.4
            + lexical_diversity * 0.3
        )

        # 4. AMABILIDAD
        total_comments = 0
        for post in posts:
            if isinstance(post, dict):
                comments = post.get("comments", 0)
                if isinstance(comments, (int, float)):
                    total_comments += comments

        agreeableness_score = (
            (sentiment["positive"] / max(sentiment["total_texts_analyzed"], 1)) * 0.4
            + self.calculate_word_frequency(posts_text, self.agreeableness_words) * 0.4
            + min(total_comments / max(len(posts_text), 1) / 10, 1.0)
            * 0.2  # Normalizar comentarios
        )

        # 5. RESPONSABILIDAD
        basic_info = data.get("basic_info", {})
        bio_text = basic_info.get("bio", "") if isinstance(basic_info, dict) else ""

        conscientiousness_score = (
            self.calculate_word_frequency(posts_text, self.conscientiousness_words)
            * 0.6
            + (1.0 if len(posts_text) >= 5 else 0.3)
            * 0.2  # Consistencia (mínimo 5 posts)
            + (1.0 if bio_text and len(bio_text.strip()) > 20 else 0.3)
            * 0.2  # Biografía completa
        )

        # Normalizar scores a 0-1
        scores = {
            "extraversion": min(max(extraversion_score, 0.0), 1.0),
            "neuroticism": min(max(neuroticism_score, 0.0), 1.0),
            "openness": min(max(openness_score, 0.0), 1.0),
            "agreeableness": min(max(agreeableness_score, 0.0), 1.0),
            "conscientiousness": min(max(conscientiousness_score, 0.0), 1.0),
        }

        # Almacenar resultados
        self.results = {
            "big_five_scores": scores,
            "metadata": {
                "posts_analyzed": len(posts_text),
                "words_analyzed": len(words),
                "unique_words": len(set(words)) if words else 0,
                "lexical_diversity": round(lexical_diversity, 3),
                "sentiment_analysis": sentiment,
            },
            "calculated_components": {
                "extraversion": {
                    "friends_normalized": min(friends_count / 1000, 1.0),
                    "reactions_per_post": total_reactions / max(len(posts_text), 1),
                    "word_frequency": self.calculate_word_frequency(
                        posts_text, self.extraversion_words
                    ),
                },
                "neuroticism": {
                    "negative_ratio": sentiment["negative"]
                    / max(sentiment["total_texts_analyzed"], 1),
                    "sentiment_balance": sentiment["sentiment_balance"],
                    "word_frequency": self.calculate_word_frequency(
                        posts_text, self.neuroticism_words
                    ),
                },
            },
        }

        return scores

    def _get_default_scores(self) -> Dict[str, float]:
        """Retorna scores por defecto cuando no hay datos"""
        default_scores = {
            "extraversion": 0.5,
            "neuroticism": 0.5,
            "openness": 0.5,
            "agreeableness": 0.5,
            "conscientiousness": 0.5,
        }

        self.results = {
            "big_five_scores": default_scores,
            "metadata": {
                "posts_analyzed": 0,
                "words_analyzed": 0,
                "unique_words": 0,
                "lexical_diversity": 0.0,
                "sentiment_analysis": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "avg_polarity": 0.0,
                    "sentiment_balance": 0.5,
                    "total_texts_analyzed": 0,
                },
            },
        }

        return default_scores

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
                "conscientiousness": f"Responsabilidad ({score:.2f}): {level}. ",
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
        report.append("=" * 60)
        report.append("📊 INFORME DE ANÁLISIS DE PERSONALIDAD (BIG FIVE)")
        report.append("=" * 60)
        report.append("")

        # Metadatos
        report.append(f"📈 METADATOS DEL ANÁLISIS:")
        report.append(
            f"   • Publicaciones analizadas: {metadata.get('posts_analyzed', 0)}"
        )
        report.append(
            f"   • Palabras analizadas: {metadata.get('words_analyzed', 0):,}"
        )
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
            "conscientiousness": ("Responsabilidad", "Organización vs. espontaneidad"),
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

            report.append(
                f"   {trait_name.upper():20} {score:.2f} {bar} ({interpretation})"
            )
            report.append(f"     ↳ {description}")

        report.append("")
        report.append("📋 INTERPRETACIÓN:")
        report.append("")

        # Análisis de sentimiento
        sentiment = metadata.get("sentiment_analysis", {})
        if sentiment:
            report.append(f"1. SENTIMIENTO GENERAL:")
            report.append(f"   Publicaciones positivas: {sentiment.get('positive', 0)}")
            report.append(f"   Publicaciones negativas: {sentiment.get('negative', 0)}")
            report.append(f"   Publicaciones neutrales: {sentiment.get('neutral', 0)}")
            report.append(
                f"   Polaridad promedio: {sentiment.get('avg_polarity', 0):.3f}"
            )
            report.append("")

        report.append("=" * 60)
        report.append("⚠️  NOTA: Este análisis es aproximado y con fines académicos.")
        report.append(
            "    Para evaluación psicológica profesional, consulte a un especialista."
        )
        report.append("=" * 60)

        return "\n".join(report)

    def save_results(self, filename: str = "big5_analysis.json"):
        """Guarda los resultados en un archivo JSON y el reporte en texto."""
        if not self.results:
            print(
                "No hay resultados para guardar. Ejecute calculate_big_five_scores primero."
            )
            return

        output_path = Path("data/results") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"💾 Resultados guardados en: {output_path}")

        # Guardar también reporte en texto
        txt_path = output_path.with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(self.generate_report())

        print(f"📄 Reporte guardado en: {txt_path}")
