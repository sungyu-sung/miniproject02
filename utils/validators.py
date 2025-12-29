"""검증 유틸리티"""
import re
from urllib.parse import urlparse
from typing import Tuple


class URLValidator:
    """URL 검증 클래스"""

    # 지원하는 뉴스 도메인
    SUPPORTED_NEWS_DOMAINS = [
        'naver.com',
        'daum.net',
        'chosun.com',
        'donga.com',
        'joongang.co.kr',
        'hani.co.kr',
        'khan.co.kr',
        'yonhapnews.co.kr',
        'yna.co.kr',
        'mk.co.kr',
        'hankyung.com',
        'mt.co.kr',
        'sedaily.com',
        'etnews.com',
        'zdnet.co.kr',
        'itworld.co.kr'
    ]

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """URL 유효성 검사"""
        try:
            result = urlparse(url)
            return all([
                result.scheme in ('http', 'https'),
                result.netloc
            ])
        except Exception:
            return False

    @classmethod
    def is_news_url(cls, url: str) -> Tuple[bool, str]:
        """
        뉴스 URL인지 확인

        Returns:
            Tuple[bool, str]: (뉴스 URL 여부, 메시지)
        """
        if not cls.is_valid_url(url):
            return False, "올바른 URL 형식이 아닙니다."

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # www 제거
        if domain.startswith('www.'):
            domain = domain[4:]

        # 지원 도메인 확인
        for supported in cls.SUPPORTED_NEWS_DOMAINS:
            if supported in domain:
                return True, f"지원되는 뉴스 사이트입니다: {supported}"

        return True, "뉴스 URL로 인식됩니다. (크롤링 시도)"

    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """URL 정리"""
        url = url.strip()

        # 프로토콜 추가
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return url

    @classmethod
    def extract_domain(cls, url: str) -> str:
        """도메인 추출"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""


class TextValidator:
    """텍스트 검증 클래스"""

    MIN_TEXT_LENGTH = 50
    MAX_TEXT_LENGTH = 50000

    @classmethod
    def is_valid_article_text(cls, text: str) -> Tuple[bool, str]:
        """
        기사 본문 유효성 검사

        Returns:
            Tuple[bool, str]: (유효 여부, 메시지)
        """
        if not text:
            return False, "텍스트가 비어있습니다."

        text = text.strip()

        if len(text) < cls.MIN_TEXT_LENGTH:
            return False, f"텍스트가 너무 짧습니다. (최소 {cls.MIN_TEXT_LENGTH}자)"

        if len(text) > cls.MAX_TEXT_LENGTH:
            return False, f"텍스트가 너무 깁니다. (최대 {cls.MAX_TEXT_LENGTH}자)"

        # 한글 포함 여부 확인
        korean_chars = len(re.findall(r'[가-힣]', text))
        korean_ratio = korean_chars / len(text)

        if korean_ratio < 0.1:
            return False, "한국어 콘텐츠가 거의 없습니다."

        return True, "유효한 텍스트입니다."

    @classmethod
    def estimate_read_time(cls, text: str) -> int:
        """예상 읽기 시간 계산 (분)"""
        # 평균 읽기 속도: 분당 500자 (한국어)
        char_count = len(text)
        minutes = char_count / 500
        return max(1, round(minutes))
