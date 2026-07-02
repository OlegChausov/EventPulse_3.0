import re
from unidecode import unidecode

class QueryNormalizer:
    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        text = text.replace("ё", "е")
        return text

    @classmethod
    def for_concert(cls, text: str) -> str:
        base = cls.normalize(text)
        return unidecode(base)  # транслитерация для артистов

    @classmethod
    def for_film(cls, text: str) -> str:
        return cls.normalize(text)  # оставляем кириллицу

    @classmethod
    def preprocess(cls, text: str, query_type: str) -> str:
        if query_type == "concert":
            return cls.for_concert(text)
        elif query_type == "film":
            return cls.for_film(text)
        else:
            return cls.normalize(text)  # fallback
