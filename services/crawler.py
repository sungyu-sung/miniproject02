"""뉴스 크롤링 서비스"""
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

from models.schemas import ArticleData
import logging

logger = logging.getLogger(__name__)


class CrawlerService:
    """뉴스 기사 크롤링 서비스"""

    # 지원하는 뉴스 사이트 패턴
    SUPPORTED_SITES = {
        "naver.com": "네이버 뉴스",
        "daum.net": "다음 뉴스",
        "chosun.com": "조선일보",
        "donga.com": "동아일보",
        "joongang.co.kr": "중앙일보",
        "hani.co.kr": "한겨레",
        "khan.co.kr": "경향신문",
        "yonhapnews.co.kr": "연합뉴스"
    }

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def extract_article(self, url: str) -> ArticleData:
        """
        뉴스 URL에서 기사 정보 추출

        Args:
            url: 뉴스 기사 URL

        Returns:
            ArticleData: 추출된 기사 데이터
        """
        # newspaper3k 사용 시도
        if NEWSPAPER_AVAILABLE:
            try:
                return self._extract_with_newspaper(url)
            except Exception as e:
                logger.warning(f"newspaper3k 추출 실패: {e}, BeautifulSoup으로 시도")

        # 폴백: BeautifulSoup 사용
        return self._extract_with_beautifulsoup(url)

    def _extract_with_newspaper(self, url: str) -> ArticleData:
        """newspaper3k를 사용한 추출"""
        article = Article(url, language='ko')
        article.download()
        article.parse()

        return ArticleData(
            title=article.title or "제목 없음",
            content=article.text or "",
            date=article.publish_date,
            image_url=article.top_image,
            source=self._get_source_name(url),
            url=url
        )

    def _extract_with_beautifulsoup(self, url: str) -> ArticleData:
        """BeautifulSoup을 사용한 추출 (폴백)"""
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # 제목 추출
        title = self._extract_title(soup)

        # 본문 추출
        content = self._extract_content(soup, url)

        # 날짜 추출
        date = self._extract_date(soup)

        # 이미지 추출
        image_url = self._extract_image(soup)

        return ArticleData(
            title=title,
            content=content,
            date=date,
            image_url=image_url,
            source=self._get_source_name(url),
            url=url
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        # 일반적인 제목 태그들
        title_selectors = [
            'h1.article_title',
            'h1.tit_view',
            'h1#articleTitle',
            'h1.news_ttl',
            'meta[property="og:title"]',
            'title'
        ]

        for selector in title_selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    return elem['content']
            else:
                elem = soup.select_one(selector)
                if elem:
                    return elem.get_text(strip=True)

        return "제목 없음"

    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """본문 추출"""
        # 네이버 뉴스
        if 'naver.com' in url:
            content_elem = soup.select_one('#dic_area, #articleBodyContents, .article_body')
        # 다음 뉴스
        elif 'daum.net' in url:
            content_elem = soup.select_one('.article_view, #dmcfContents')
        # 일반적인 경우
        else:
            content_elem = soup.select_one('article, .article-body, .article_content, #article-body')

        if content_elem:
            # 불필요한 태그 제거
            for tag in content_elem.select('script, style, iframe, .ad'):
                tag.decompose()
            return self._clean_text(content_elem.get_text())

        # 폴백: p 태그들 수집
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50)
        return self._clean_text(content)

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """날짜 추출"""
        date_selectors = [
            'meta[property="article:published_time"]',
            'time[datetime]',
            '.article_date',
            '.date'
        ]

        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                date_str = elem.get('content') or elem.get('datetime') or elem.get_text()
                try:
                    # ISO 형식 시도
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass

        return None

    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """대표 이미지 추출"""
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image and og_image.get('content'):
            return og_image['content']

        article_img = soup.select_one('article img, .article_body img')
        if article_img and article_img.get('src'):
            return article_img['src']

        return None

    def _get_source_name(self, url: str) -> str:
        """URL에서 언론사 이름 추출"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for site_domain, name in self.SUPPORTED_SITES.items():
            if site_domain in domain:
                return name

        return domain

    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 연속 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 앞뒤 공백 제거
        text = text.strip()
        return text

    def is_valid_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except:
            return False
