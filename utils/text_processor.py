"""텍스트 전처리 유틸리티"""
import re
from typing import List


class TextProcessor:
    """텍스트 전처리 클래스"""

    @staticmethod
    def clean_text(text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""

        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)

        # 특수 문자 정리 (한글, 영어, 숫자, 기본 문장부호만 유지)
        text = re.sub(r'[^\w\s가-힣.,!?\'\"()-]', ' ', text)

        # 연속 공백 제거
        text = re.sub(r'\s+', ' ', text)

        # 연속 마침표 정리
        text = re.sub(r'\.{2,}', '.', text)

        return text.strip()

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """문장 분리"""
        # 한국어 문장 구분
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """텍스트 길이 제한"""
        if len(text) <= max_length:
            return text

        # 단어 경계에서 자르기
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')

        if last_space > max_length * 0.8:
            truncated = truncated[:last_space]

        return truncated.rstrip() + suffix

    @staticmethod
    def remove_urls(text: str) -> str:
        """URL 제거"""
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '', text)

    @staticmethod
    def remove_emails(text: str) -> str:
        """이메일 제거"""
        email_pattern = r'\S+@\S+\.\S+'
        return re.sub(email_pattern, '', text)

    @staticmethod
    def extract_numbers(text: str) -> List[str]:
        """숫자 추출"""
        return re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', text)

    @staticmethod
    def count_words(text: str) -> int:
        """단어 수 계산"""
        # 한국어: 공백 기준
        # 영어: 공백 기준
        words = text.split()
        return len(words)

    @staticmethod
    def count_characters(text: str, include_spaces: bool = False) -> int:
        """문자 수 계산"""
        if include_spaces:
            return len(text)
        return len(text.replace(' ', ''))

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """공백 정규화"""
        # 탭, 개행 등을 공백으로
        text = re.sub(r'[\t\n\r\f\v]+', ' ', text)
        # 연속 공백 제거
        text = re.sub(r' +', ' ', text)
        return text.strip()
