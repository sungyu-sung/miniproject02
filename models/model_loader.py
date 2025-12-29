"""Hugging Face 모델 로더"""
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    pipeline
)
from typing import Optional, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelLoader:
    """Hugging Face 모델 로딩 및 관리 클래스"""

    # 모델 ID 상수
    SUMMARIZATION_MODEL = "gogamza/kobart-summarization"
    SENTIMENT_MODEL = "snunlp/KR-FinBert-SC"
    EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # 캐시된 모델들
        self._summarizer = None
        self._sentiment_analyzer = None
        self._embedding_model = None

    @property
    def summarizer(self) -> Tuple[Any, Any]:
        """요약 모델 로드 (지연 로딩)"""
        if self._summarizer is None:
            logger.info(f"Loading summarization model: {self.SUMMARIZATION_MODEL}")
            tokenizer = AutoTokenizer.from_pretrained(self.SUMMARIZATION_MODEL)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.SUMMARIZATION_MODEL)
            model = model.to(self.device)
            self._summarizer = (tokenizer, model)
            logger.info("Summarization model loaded successfully")
        return self._summarizer

    @property
    def sentiment_analyzer(self) -> Any:
        """감정 분석 파이프라인 로드 (지연 로딩)"""
        if self._sentiment_analyzer is None:
            logger.info(f"Loading sentiment model: {self.SENTIMENT_MODEL}")
            self._sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=self.SENTIMENT_MODEL,
                tokenizer=self.SENTIMENT_MODEL,
                device=0 if self.device == "cuda" else -1,
                max_length=512,
                truncation=True
            )
            logger.info("Sentiment model loaded successfully")
        return self._sentiment_analyzer

    @property
    def embedding_model(self) -> Any:
        """임베딩 모델 로드 (키워드 추출용)"""
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {self.EMBEDDING_MODEL}")
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer(self.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        return self._embedding_model

    def get_model_info(self) -> dict:
        """로드된 모델 정보 반환"""
        return {
            "summarization": self.SUMMARIZATION_MODEL,
            "sentiment": self.SENTIMENT_MODEL,
            "embedding": self.EMBEDDING_MODEL,
            "device": self.device
        }


# 싱글톤 인스턴스
_model_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    """ModelLoader 싱글톤 인스턴스 반환"""
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader
