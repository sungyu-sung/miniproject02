"""결과 표시 컴포넌트"""
import streamlit as st
from typing import List
from models.schemas import (
    ArticleData,
    SummaryResult,
    SentimentResult,
    KeywordResult,
    AnalysisResult
)


def render_article_info(article: ArticleData):
    """기사 정보 표시"""
    st.subheader("원문 정보")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**제목:** {article.title}")
        if article.source:
            st.caption(f"출처: {article.source}")

    with col2:
        if article.date:
            st.caption(f"작성일: {article.date.strftime('%Y-%m-%d')}")

    # 본문 미리보기
    with st.expander("원문 보기", expanded=False):
        st.text_area(
            "본문",
            value=article.content[:2000] + ("..." if len(article.content) > 2000 else ""),
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )
        st.caption(f"전체 {len(article.content):,}자")


def render_summary(summary: SummaryResult):
    """요약 결과 표시"""
    st.subheader("요약 결과")

    st.info(summary.summary)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("원문 길이", f"{summary.original_length:,}자")
    with col2:
        st.metric("요약 길이", f"{summary.summary_length:,}자")
    with col3:
        st.metric("압축률", f"{summary.compression_ratio}%")


def render_sentiment(sentiment: SentimentResult):
    """감정 분석 결과 표시"""
    st.subheader("감정 분석")

    # 라벨 및 이모지
    col1, col2 = st.columns([1, 2])

    with col1:
        label_color = {
            "긍정": "green",
            "부정": "red",
            "중립": "gray"
        }.get(sentiment.label, "gray")

        st.markdown(
            f"<h2 style='text-align: center;'>{sentiment.label_emoji}</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='text-align: center; color: {label_color}; font-weight: bold;'>{sentiment.label}</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='text-align: center;'>신뢰도: {int(sentiment.confidence * 100)}%</p>",
            unsafe_allow_html=True
        )

    with col2:
        # 점수 바 차트
        for label, score in sentiment.scores.items():
            color = {
                "긍정": "#28a745",
                "부정": "#dc3545",
                "중립": "#6c757d"
            }.get(label, "#6c757d")

            st.markdown(f"**{label}**")
            st.progress(score)
            st.caption(f"{int(score * 100)}%")


def render_keywords(keywords: List[KeywordResult]):
    """키워드 표시"""
    st.subheader("주요 키워드")

    if not keywords:
        st.info("추출된 키워드가 없습니다.")
        return

    # 태그 형태로 표시
    tags_html = " ".join([
        f'<span style="background-color: #e3f2fd; padding: 5px 10px; '
        f'border-radius: 15px; margin: 2px; display: inline-block;">'
        f'#{kw.keyword}</span>'
        for kw in keywords
    ])
    st.markdown(tags_html, unsafe_allow_html=True)

    # 점수와 함께 표시
    with st.expander("키워드 상세 점수", expanded=False):
        for kw in keywords:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(kw.keyword)
            with col2:
                st.progress(kw.score)


def render_full_results(result: AnalysisResult):
    """전체 분석 결과 표시"""
    # 기사 정보
    render_article_info(result.article)

    st.divider()

    # 2열 레이아웃
    col1, col2 = st.columns(2)

    with col1:
        render_summary(result.summary)

    with col2:
        render_sentiment(result.sentiment)

    st.divider()

    # 키워드
    render_keywords(result.keywords)

    # 분석 시간
    if result.analyzed_at:
        st.caption(f"분석 시간: {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")


def render_loading():
    """로딩 상태 표시"""
    with st.spinner("분석 중입니다..."):
        st.info("뉴스 기사를 분석하고 있습니다. 잠시만 기다려주세요.")


def render_error(message: str):
    """에러 표시"""
    st.error(f"오류가 발생했습니다: {message}")
