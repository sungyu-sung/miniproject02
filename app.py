"""
뉴스 요약 및 감정 분석 챗봇
Hugging Face 모델을 활용한 한국어 뉴스 분석 시스템
"""
import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from services.crawler import CrawlerService
from services.summarizer import SummarizerService
from services.sentiment import SentimentService
from services.keywords import KeywordService
from models.schemas import AnalysisResult
from utils.validators import URLValidator, TextValidator
from components.sidebar import render_sidebar, add_to_history
from components.result_display import (
    render_full_results,
    render_loading,
    render_error
)
from components.charts import (
    render_sentiment_chart,
    render_keyword_bar_chart
)

# 페이지 설정
st.set_page_config(
    page_title="뉴스 요약 & 감정 분석",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .result-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# 서비스 초기화 (캐싱)
@st.cache_resource
def init_services():
    """서비스 초기화"""
    return {
        "crawler": CrawlerService(),
        "summarizer": SummarizerService(),
        "sentiment": SentimentService(),
        "keywords": KeywordService()
    }


def analyze_news(url: str, settings: dict) -> AnalysisResult:
    """뉴스 분석 수행"""
    services = init_services()

    # 1. 기사 크롤링
    with st.status("뉴스 기사 수집 중...", expanded=True) as status:
        st.write("URL에서 기사 본문을 추출하고 있습니다...")
        article = services["crawler"].extract_article(url)

        if not article.content:
            raise ValueError("기사 본문을 추출할 수 없습니다.")

        st.write(f"✅ 기사 수집 완료: {len(article.content):,}자")
        status.update(label="기사 수집 완료!", state="complete")

    # 2. 텍스트 검증
    is_valid, message = TextValidator.is_valid_article_text(article.content)
    if not is_valid:
        raise ValueError(message)

    # 3. 요약
    with st.status("요약 생성 중...", expanded=True) as status:
        st.write("AI 모델이 기사를 요약하고 있습니다...")
        summary = services["summarizer"].summarize(
            article.content,
            max_length=settings["max_summary_length"],
            min_length=settings["min_summary_length"]
        )
        st.write(f"✅ 요약 완료: {summary.summary_length}자")
        status.update(label="요약 완료!", state="complete")

    # 4. 감정 분석
    with st.status("감정 분석 중...", expanded=True) as status:
        st.write("기사의 감정을 분석하고 있습니다...")
        sentiment = services["sentiment"].analyze(article.content)
        st.write(f"✅ 감정 분석 완료: {sentiment.label} ({int(sentiment.confidence * 100)}%)")
        status.update(label="감정 분석 완료!", state="complete")

    # 5. 키워드 추출
    with st.status("키워드 추출 중...", expanded=True) as status:
        st.write("주요 키워드를 추출하고 있습니다...")
        keywords = services["keywords"].extract(
            article.content,
            top_k=settings["keyword_count"]
        )
        st.write(f"✅ 키워드 추출 완료: {len(keywords)}개")
        status.update(label="키워드 추출 완료!", state="complete")

    return AnalysisResult(
        article=article,
        summary=summary,
        sentiment=sentiment,
        keywords=keywords
    )


def main():
    """메인 앱"""
    # 헤더
    st.markdown('<p class="main-header">📰 뉴스 요약 & 감정 분석 챗봇</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">뉴스 URL을 입력하면 AI가 요약하고 감정을 분석해드립니다.</p>',
        unsafe_allow_html=True
    )

    # 세션 상태 초기화
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "current_result" not in st.session_state:
        st.session_state.current_result = None

    # 사이드바
    settings = render_sidebar(st.session_state.analysis_history)

    # 메인 영역
    col1, col2 = st.columns([4, 1])

    with col1:
        url_input = st.text_input(
            "뉴스 URL 입력",
            placeholder="https://news.naver.com/article/...",
            help="분석할 뉴스 기사의 URL을 입력하세요."
        )

    with col2:
        st.write("")  # 정렬을 위한 공백
        st.write("")
        analyze_button = st.button("🔍 분석하기", type="primary")

    # 분석 실행
    if analyze_button and url_input:
        # URL 검증
        url = URLValidator.sanitize_url(url_input)

        if not URLValidator.is_valid_url(url):
            st.error("올바른 URL 형식을 입력해주세요.")
        else:
            is_news, message = URLValidator.is_news_url(url)
            st.info(message)

            try:
                # 분석 수행
                result = analyze_news(url, settings)
                st.session_state.current_result = result

                # 히스토리에 추가
                add_to_history(
                    st.session_state,
                    title=result.article.title,
                    url=url,
                    sentiment=result.sentiment.label,
                    summary=result.summary.summary[:100]
                )

                st.success("분석이 완료되었습니다!")

            except Exception as e:
                render_error(str(e))

    # 결과 표시
    if st.session_state.current_result:
        st.divider()
        render_full_results(st.session_state.current_result)

        # 추가 시각화
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("감정 분포")
            render_sentiment_chart(st.session_state.current_result.sentiment)

        with col2:
            st.subheader("키워드 중요도")
            render_keyword_bar_chart(st.session_state.current_result.keywords)

    # 사용 안내 (결과가 없을 때)
    if not st.session_state.current_result:
        st.divider()

        st.subheader("사용 방법")
        st.markdown("""
        1. **뉴스 URL 입력**: 분석하고 싶은 뉴스 기사의 URL을 입력합니다.
        2. **분석하기 클릭**: AI가 자동으로 기사를 분석합니다.
        3. **결과 확인**: 요약, 감정 분석, 키워드를 확인합니다.

        **지원 뉴스 사이트:**
        - 네이버 뉴스, 다음 뉴스
        - 조선일보, 동아일보, 중앙일보
        - 한겨레, 경향신문, 연합뉴스
        - 그 외 대부분의 뉴스 사이트
        """)

        st.info("💡 Tip: 사이드바에서 요약 길이와 키워드 개수를 조절할 수 있습니다.")


if __name__ == "__main__":
    main()
