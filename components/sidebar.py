"""사이드바 컴포넌트"""
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime


def render_sidebar(history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    사이드바 렌더링

    Args:
        history: 분석 히스토리 목록

    Returns:
        Dict[str, Any]: 사이드바 설정값
    """
    with st.sidebar:
        st.header("설정")

        # 요약 설정
        st.subheader("요약 설정")
        max_summary_length = st.slider(
            "최대 요약 길이",
            min_value=50,
            max_value=300,
            value=150,
            step=10,
            help="요약문의 최대 길이를 설정합니다."
        )

        min_summary_length = st.slider(
            "최소 요약 길이",
            min_value=30,
            max_value=100,
            value=50,
            step=10,
            help="요약문의 최소 길이를 설정합니다."
        )

        # 키워드 설정
        st.subheader("키워드 설정")
        keyword_count = st.selectbox(
            "추출할 키워드 수",
            options=[3, 5, 7, 10],
            index=1,
            help="기사에서 추출할 키워드 개수를 선택합니다."
        )

        st.divider()

        # 분석 히스토리
        st.subheader("분석 히스토리")

        if history and len(history) > 0:
            for i, item in enumerate(history[-5:]):  # 최근 5개만
                with st.expander(
                    f"{item.get('title', '제목 없음')[:20]}...",
                    expanded=False
                ):
                    st.caption(f"분석 시간: {item.get('time', 'N/A')}")
                    st.caption(f"감정: {item.get('sentiment', 'N/A')}")
                    if st.button("다시 보기", key=f"history_{i}"):
                        st.session_state.selected_history = item
        else:
            st.info("분석 히스토리가 없습니다.")

        st.divider()

        # 모델 정보
        st.subheader("모델 정보")
        st.caption("**요약 모델**")
        st.code("gogamza/kobart-summarization", language=None)

        st.caption("**감정 분석 모델**")
        st.code("snunlp/KR-FinBert-SC", language=None)

        st.caption("**키워드 추출**")
        st.code("KeyBERT + ko-sroberta", language=None)

        st.divider()

        # 정보
        st.caption("Made with Hugging Face & Streamlit")
        st.caption(f"Version 1.0.0")

    return {
        "max_summary_length": max_summary_length,
        "min_summary_length": min_summary_length,
        "keyword_count": keyword_count
    }


def add_to_history(
    session_state,
    title: str,
    url: str,
    sentiment: str,
    summary: str
):
    """히스토리에 분석 결과 추가"""
    if "analysis_history" not in session_state:
        session_state.analysis_history = []

    session_state.analysis_history.append({
        "title": title,
        "url": url,
        "sentiment": sentiment,
        "summary": summary,
        "time": datetime.now().strftime("%H:%M")
    })

    # 최대 20개까지만 유지
    if len(session_state.analysis_history) > 20:
        session_state.analysis_history = session_state.analysis_history[-20:]
