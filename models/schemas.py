"""데이터 스키마 정의"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class ArticleData:
    """크롤링된 기사 데이터"""
    title: str
    content: str
    date: Optional[datetime] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    url: str = ""

    @property
    def content_length(self) -> int:
        return len(self.content)


@dataclass
class SummaryResult:
    """요약 결과"""
    summary: str
    original_length: int
    summary_length: int

    @property
    def compression_ratio(self) -> float:
        """압축률 계산 (%)"""
        if self.original_length == 0:
            return 0.0
        return round((1 - self.summary_length / self.original_length) * 100, 1)


@dataclass
class SentimentResult:
    """감정 분석 결과"""
    label: str  # "긍정", "부정", "중립"
    confidence: float  # 0.0 ~ 1.0
    scores: Dict[str, float]  # 각 라벨별 점수

    @property
    def label_emoji(self) -> str:
        """라벨에 맞는 이모지 반환"""
        emoji_map = {
            "긍정": "😊",
            "부정": "😟",
            "중립": "😐"
        }
        return emoji_map.get(self.label, "❓")


@dataclass
class KeywordResult:
    """키워드 추출 결과"""
    keyword: str
    score: float  # 중요도 점수


@dataclass
class AnalysisResult:
    """전체 분석 결과"""
    article: ArticleData
    summary: SummaryResult
    sentiment: SentimentResult
    keywords: List[KeywordResult]
    analyzed_at: datetime = None

    def __post_init__(self):
        if self.analyzed_at is None:
            self.analyzed_at = datetime.now()
