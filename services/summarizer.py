"""텍스트 요약 서비스"""
import torch
from typing import Optional
import logging

from models.schemas import SummaryResult
from models.model_loader import get_model_loader

logger = logging.getLogger(__name__)


class SummarizerService:
    """KoBART 기반 텍스트 요약 서비스"""

    def __init__(self):
        self.model_loader = get_model_loader()
        self.max_input_length = 1024
        self.min_output_length = 50
        self.max_output_length = 150

    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> SummaryResult:
        """
        텍스트 요약 수행

        Args:
            text: 요약할 텍스트
            max_length: 최대 출력 길이
            min_length: 최소 출력 길이

        Returns:
            SummaryResult: 요약 결과
        """
        if not text or len(text.strip()) == 0:
            return SummaryResult(
                summary="요약할 텍스트가 없습니다.",
                original_length=0,
                summary_length=0
            )

        max_len = max_length or self.max_output_length
        min_len = min_length or self.min_output_length

        original_length = len(text)

        try:
            tokenizer, model = self.model_loader.summarizer
            device = self.model_loader.device

            # 텍스트 전처리
            text = self._preprocess(text)

            # 토큰화
            inputs = tokenizer(
                text,
                return_tensors="pt",
                max_length=self.max_input_length,
                truncation=True,
                padding=True
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # 요약 생성
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=max_len,
                    min_length=min_len,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3
                )

            # 디코딩
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summary = self._postprocess(summary)

            return SummaryResult(
                summary=summary,
                original_length=original_length,
                summary_length=len(summary)
            )

        except Exception as e:
            logger.error(f"요약 생성 실패: {e}")
            return SummaryResult(
                summary=f"요약 생성 중 오류가 발생했습니다: {str(e)}",
                original_length=original_length,
                summary_length=0
            )

    def summarize_long_text(self, text: str, chunk_size: int = 1000) -> SummaryResult:
        """
        긴 텍스트를 청크로 나누어 요약

        Args:
            text: 요약할 긴 텍스트
            chunk_size: 청크 크기

        Returns:
            SummaryResult: 통합된 요약 결과
        """
        original_length = len(text)

        if len(text) <= chunk_size:
            return self.summarize(text)

        # 텍스트를 청크로 분할
        chunks = self._split_into_chunks(text, chunk_size)
        logger.info(f"텍스트를 {len(chunks)}개 청크로 분할")

        # 각 청크 요약
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"청크 {i+1}/{len(chunks)} 요약 중...")
            result = self.summarize(chunk, max_length=100)
            chunk_summaries.append(result.summary)

        # 청크 요약들을 다시 요약
        combined_text = " ".join(chunk_summaries)
        final_result = self.summarize(combined_text)

        return SummaryResult(
            summary=final_result.summary,
            original_length=original_length,
            summary_length=len(final_result.summary)
        )

    def _preprocess(self, text: str) -> str:
        """텍스트 전처리"""
        # 불필요한 공백 제거
        text = ' '.join(text.split())
        return text

    def _postprocess(self, summary: str) -> str:
        """요약 후처리"""
        # 문장 끝 정리
        summary = summary.strip()
        if summary and not summary.endswith(('.', '다', '요', '!')):
            summary += '.'
        return summary

    def _split_into_chunks(self, text: str, chunk_size: int) -> list:
        """텍스트를 문장 단위로 청크 분할"""
        import re

        # 문장 분리
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
