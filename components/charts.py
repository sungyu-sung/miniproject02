"""차트 컴포넌트"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from models.schemas import SentimentResult, KeywordResult


def render_sentiment_chart(sentiment: SentimentResult):
    """감정 분석 파이 차트"""
    # 데이터 준비
    labels = list(sentiment.scores.keys())
    values = list(sentiment.scores.values())

    # 색상 설정
    colors = {
        "긍정": "#28a745",
        "부정": "#dc3545",
        "중립": "#6c757d"
    }
    chart_colors = [colors.get(label, "#6c757d") for label in labels]

    # 파이 차트 생성
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=chart_colors,
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_gauge(sentiment: SentimentResult):
    """감정 분석 게이지 차트"""
    # 긍정-부정 스케일 (-1 ~ 1)
    score = sentiment.scores.get("긍정", 0) - sentiment.scores.get("부정", 0)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [-1, 1], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.3], 'color': "#ffcccb"},
                {'range': [-0.3, 0.3], 'color': "#f0f0f0"},
                {'range': [0.3, 1], 'color': "#90EE90"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        },
        title={'text': "감정 지수"}
    ))

    fig.update_layout(
        height=250,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_keyword_bar_chart(keywords: List[KeywordResult]):
    """키워드 막대 차트"""
    if not keywords:
        return

    # 데이터 준비
    kw_data = {
        "키워드": [kw.keyword for kw in keywords],
        "중요도": [kw.score for kw in keywords]
    }

    # 막대 차트 생성
    fig = px.bar(
        kw_data,
        x="중요도",
        y="키워드",
        orientation='h',
        color="중요도",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)


def render_word_cloud_placeholder(keywords: List[KeywordResult]):
    """워드클라우드 대체 표시 (실제 워드클라우드는 추가 라이브러리 필요)"""
    if not keywords:
        return

    # 크기에 따른 폰트 사이즈 계산
    max_score = max(kw.score for kw in keywords) if keywords else 1

    html_parts = []
    for kw in keywords:
        size = int(16 + (kw.score / max_score) * 24)  # 16px ~ 40px
        opacity = 0.5 + (kw.score / max_score) * 0.5  # 0.5 ~ 1.0
        html_parts.append(
            f'<span style="font-size: {size}px; opacity: {opacity}; '
            f'margin: 5px; display: inline-block; color: #1976d2;">'
            f'{kw.keyword}</span>'
        )

    html = f'<div style="text-align: center;">{"".join(html_parts)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_summary_comparison(original_length: int, summary_length: int):
    """요약 비교 차트"""
    fig = go.Figure(data=[
        go.Bar(name='원문', x=['길이'], y=[original_length], marker_color='lightgray'),
        go.Bar(name='요약', x=['길이'], y=[summary_length], marker_color='steelblue')
    ])

    fig.update_layout(
        barmode='group',
        height=200,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
