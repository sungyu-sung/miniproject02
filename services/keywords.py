"""키워드 추출 서비스"""
from typing import List
import logging
import re

from models.schemas import KeywordResult
from models.model_loader import get_model_loader

logger = logging.getLogger(__name__)


class KeywordService:
    """한국어 키워드 추출 서비스"""

    # 불용어 목록
    STOPWORDS = {
        '있다', '하다', '되다', '이다', '않다', '없다', '같다', '보다',
        '대한', '통해', '위해', '따라', '관련', '대해', '가장', '또한',
        '그리고', '하지만', '그러나', '따라서', '그래서', '때문에',
        '것으로', '것이다', '것이며', '수도', '가능', '있는', '하는',
        '이번', '지난', '오늘', '내일', '어제', '올해', '작년', '내년'
    }

    def __init__(self):
        self.model_loader = get_model_loader()

    def extract(self, text: str, top_k: int = 5) -> List[KeywordResult]:
        """
        텍스트에서 키워드 추출

        Args:
            text: 키워드를 추출할 텍스트
            top_k: 추출할 키워드 개수

        Returns:
            List[KeywordResult]: 키워드 목록
        """
        if not text or len(text.strip()) == 0:
            return []

        try:
            return self._extract_with_keybert(text, top_k)
        except Exception as e:
            logger.warning(f"KeyBERT 추출 실패: {e}, 폴백 방법 사용")
            return self._extract_with_frequency(text, top_k)

    def _extract_with_keybert(self, text: str, top_k: int) -> List[KeywordResult]:
        """KeyBERT를 사용한 키워드 추출"""
        from keybert import KeyBERT

        # 임베딩 모델 로드
        embedding_model = self.model_loader.embedding_model

        # KeyBERT 초기화
        kw_model = KeyBERT(model=embedding_model)

        # 키워드 추출
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words=list(self.STOPWORDS),
            top_n=top_k * 2,  # 필터링을 위해 더 많이 추출
            use_mmr=True,
            diversity=0.5
        )

        # 결과 필터링 및 변환
        results = []
        for keyword, score in keywords:
            # 불용어 및 짧은 키워드 필터링
            if self._is_valid_keyword(keyword):
                results.append(KeywordResult(
                    keyword=keyword,
                    score=round(score, 4)
                ))
                if len(results) >= top_k:
                    break

        return results

    def _extract_with_frequency(self, text: str, top_k: int) -> List[KeywordResult]:
        """빈도 기반 키워드 추출 (폴백)"""
        # 한국어 단어 추출 (2글자 이상)
        words = re.findall(r'[가-힣]{2,}', text)

        # 빈도 계산
        word_freq = {}
        for word in words:
            if word not in self.STOPWORDS and len(word) >= 2:
                word_freq[word] = word_freq.get(word, 0) + 1

        # 정렬 및 상위 추출
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        results = []
        max_freq = sorted_words[0][1] if sorted_words else 1

        for word, freq in sorted_words[:top_k]:
            results.append(KeywordResult(
                keyword=word,
                score=round(freq / max_freq, 4)
            ))

        return results

    def _is_valid_keyword(self, keyword: str) -> bool:
        """키워드 유효성 검사"""
        # 너무 짧은 키워드 제외
        if len(keyword) < 2:
            return False

        # 불용어 포함 여부
        for stopword in self.STOPWORDS:
            if stopword in keyword:
                return False

        # 숫자만 있는 경우 제외
        if keyword.isdigit():
            return False

        return True

    def format_keywords_as_tags(self, keywords: List[KeywordResult]) -> str:
        """키워드를 해시태그 형식으로 포맷"""
        return " ".join(f"#{kw.keyword}" for kw in keywords)
