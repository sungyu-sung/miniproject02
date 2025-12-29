"""감정 분석 서비스"""
from typing import Dict, List
import logging

from models.schemas import SentimentResult
from models.model_loader import get_model_loader

logger = logging.getLogger(__name__)


class SentimentService:
    """한국어 감정 분석 서비스"""

    # 라벨 매핑 (모델 출력 -> 한국어)
    LABEL_MAP = {
        "positive": "긍정",
        "negative": "부정",
        "neutral": "중립",
        "LABEL_0": "부정",
        "LABEL_1": "중립",
        "LABEL_2": "긍정"
    }

    def __init__(self):
        self.model_loader = get_model_loader()
        self.max_length = 512

    def analyze(self, text: str) -> SentimentResult:
        """
        텍스트 감정 분석 수행

        Args:
            text: 분석할 텍스트

        Returns:
            SentimentResult: 감정 분석 결과
        """
        if not text or len(text.strip()) == 0:
            return SentimentResult(
                label="중립",
                confidence=0.0,
                scores={"긍정": 0.0, "부정": 0.0, "중립": 1.0}
            )

        try:
            analyzer = self.model_loader.sentiment_analyzer

            # 텍스트 전처리 및 길이 제한
            text = self._preprocess(text)

            # 텍스트가 너무 길면 분할 분석
            if len(text) > self.max_length * 2:
                return self._analyze_long_text(text)

            # 감정 분석 수행
            results = analyzer(text[:self.max_length])

            if not results:
                return SentimentResult(
                    label="중립",
                    confidence=0.0,
                    scores={"긍정": 0.0, "부정": 0.0, "중립": 1.0}
                )

            # 결과 파싱
            result = results[0]
            raw_label = result['label']
            confidence = result['score']

            # 라벨 변환
            label = self.LABEL_MAP.get(raw_label, raw_label)

            # 점수 계산 (단일 결과에서 추정)
            scores = self._estimate_scores(label, confidence)

            return SentimentResult(
                label=label,
                confidence=round(confidence, 4),
                scores=scores
            )

        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            return SentimentResult(
                label="중립",
                confidence=0.0,
                scores={"긍정": 0.0, "부정": 0.0, "중립": 1.0}
            )

    def _analyze_long_text(self, text: str) -> SentimentResult:
        """긴 텍스트 분할 분석"""
        import re

        # 문장 분리
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # 각 문장 분석
        all_scores = {"긍정": 0.0, "부정": 0.0, "중립": 0.0}
        valid_count = 0

        analyzer = self.model_loader.sentiment_analyzer

        for sentence in sentences:
            if len(sentence.strip()) < 10:
                continue

            try:
                results = analyzer(sentence[:self.max_length])
                if results:
                    raw_label = results[0]['label']
                    label = self.LABEL_MAP.get(raw_label, "중립")
                    score = results[0]['score']

                    all_scores[label] += score
                    valid_count += 1

            except Exception as e:
                logger.debug(f"문장 분석 실패: {e}")
                continue

        if valid_count == 0:
            return SentimentResult(
                label="중립",
                confidence=0.0,
                scores={"긍정": 0.0, "부정": 0.0, "중립": 1.0}
            )

        # 평균 점수 계산
        for key in all_scores:
            all_scores[key] = round(all_scores[key] / valid_count, 4)

        # 최종 라벨 결정
        final_label = max(all_scores, key=all_scores.get)
        final_confidence = all_scores[final_label]

        # 점수 정규화
        total = sum(all_scores.values())
        if total > 0:
            all_scores = {k: round(v / total, 4) for k, v in all_scores.items()}

        return SentimentResult(
            label=final_label,
            confidence=final_confidence,
            scores=all_scores
        )

    def _preprocess(self, text: str) -> str:
        """텍스트 전처리"""
        # 불필요한 공백 제거
        text = ' '.join(text.split())
        return text

    def _estimate_scores(self, label: str, confidence: float) -> Dict[str, float]:
        """단일 결과에서 전체 점수 추정"""
        scores = {"긍정": 0.0, "부정": 0.0, "중립": 0.0}

        # 주 라벨에 confidence 할당
        scores[label] = confidence

        # 나머지 라벨에 남은 점수 분배
        remaining = 1.0 - confidence
        other_labels = [l for l in scores if l != label]

        for other in other_labels:
            scores[other] = round(remaining / len(other_labels), 4)

        return scores

    def get_sentiment_description(self, result: SentimentResult) -> str:
        """감정 분석 결과 설명 생성"""
        confidence_pct = int(result.confidence * 100)

        if result.label == "긍정":
            if confidence_pct >= 80:
                return "이 기사는 매우 긍정적인 내용을 담고 있습니다."
            elif confidence_pct >= 60:
                return "이 기사는 다소 긍정적인 톤을 보입니다."
            else:
                return "이 기사는 약간 긍정적인 경향이 있습니다."

        elif result.label == "부정":
            if confidence_pct >= 80:
                return "이 기사는 매우 부정적인 내용을 담고 있습니다."
            elif confidence_pct >= 60:
                return "이 기사는 다소 부정적인 톤을 보입니다."
            else:
                return "이 기사는 약간 부정적인 경향이 있습니다."

        else:
            return "이 기사는 중립적인 톤으로 작성되었습니다."
