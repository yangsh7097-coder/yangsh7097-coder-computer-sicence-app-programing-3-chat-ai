import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="오늘의 경제 뉴스 요약",
    page_icon="📰",
    layout="wide"
)

# --- 모델 로딩 ---
# @st.cache_resource 데코레이터는 무거운 모델을 한번만 로딩하고 캐시에 저장하여
# 앱의 성능을 크게 향상시킵니다.
@st.cache_resource
def load_summarizer():
    """텍스트 요약 모델을 로드하는 함수"""
    # 한국어 요약에 특화된 모델을 사용합니다.
    summarizer = pipeline("summarization", model="gogamza/kobart-summarization")
    return summarizer

summarizer = load_summarizer()

# --- 함수 정의 ---

@st.cache_data(ttl=3600) # 1시간 동안 뉴스 목록 캐시
def get_news_feed(url):
    """RSS 피드에서 뉴스 목록을 가져오는 함수"""
    try:
        # feedparser의 내장 로직 대신 requests를 사용해 안정적으로 데이터를 가져옵니다.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # 가져온 텍스트 데이터를 feedparser로 파싱합니다.
        feed = feedparser.parse(response.content)
        return feed.entries
    except requests.exceptions.RequestException as e:
        st.error(f"RSS 피드를 가져오는 중 오류가 발생했습니다: {e}")
        return [] # 실패 시 빈 리스트 반환

def get_article_text(url, source_name):
    """뉴스 기사 URL에서 본문 텍스트를 스크레이핑하는 함수"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 발생시킴
        soup = BeautifulSoup(response.text, "html.parser")

        content = None
        # 뉴스 출처에 따라 다른 파싱 규칙 적용
        if "한국경제" in source_name:
            content = soup.find("div", id="article-body")
        elif "매일경제" in source_name:
            content = soup.find("div", id="article_body")
            # 매일경제의 경우, 본문(<p> 태그)만 정확히 추출하여 재구성합니다.
            if content:
                # 본문 영역에서 모든 p 태그를 찾아 텍스트를 합칩니다.
                # 이렇게 하면 관련기사, 기자정보 등 불필요한 div가 자동으로 제외됩니다.
                paragraphs = content.find_all('p')
                article_text = '\n'.join(p.get_text(strip=True) for p in paragraphs)
                return article_text

        if content:
            # 불필요한 태그(광고, 관련기사 링크 등) 제거
            for tag in content.find_all(['script', 'iframe', 'style', 'figure']):
                tag.decompose()
            return content.get_text(separator="\n", strip=True)

        return "기사 본문을 가져오는 데 실패했습니다. 사이트 구조가 변경되었을 수 있습니다."
    except requests.exceptions.RequestException as e:
        return f"기사를 불러오는 중 오류가 발생했습니다: {e}"

def summarize_text(text):
    """입력된 텍스트를 요약하는 함수"""
    if len(text.strip()) < 200: # 공백을 제외한 길이가 200자 미만이면 요약하지 않음
        return "요약하기에는 기사 내용이 너무 짧습니다."
    
    # 모델이 처리할 수 있는 최대 길이에 맞춰 텍스트를 자릅니다.
    max_chunk_size = 1024
    if len(text) > max_chunk_size:
        text = text[:max_chunk_size]

    try:
        summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"요약 중 오류가 발생했습니다: {e}"

# --- UI 구성 ---
st.title("📰 오늘의 경제 뉴스 요약")
st.write("RSS 피드를 통해 최신 경제 뉴스를 불러와 AI로 요약합니다.")

st.markdown("---")

# 뉴스 소스 선택
RSS_FEEDS = {
    "한국경제 (주요뉴스)": "https://www.hankyung.com/rss/major.xml",
    "매일경제 (전체기사)": "https://www.mk.co.kr/rss/all/30000001/",
}

selected_feed_name = st.sidebar.selectbox("뉴스 출처를 선택하세요:", list(RSS_FEEDS.keys()))
rss_url = RSS_FEEDS[selected_feed_name]

news_list = get_news_feed(rss_url)

if not news_list:
    st.error("뉴스 피드를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")
else:
    # 뉴스 기사 제목 목록 생성
    news_titles = [news.title for news in news_list]
    selected_title = st.selectbox("요약할 뉴스를 선택하세요:", news_titles)
    
    # 선택된 기사 정보 찾기
    selected_news = None
    for news in news_list:
        if news.title == selected_title:
            selected_news = news
            break

    if selected_news:
        st.subheader(selected_news.title)
        st.write(f"**출처:** {selected_feed_name} | **발행일:** {selected_news.get('published', 'N/A')}")
        st.markdown(f"[원문 기사 읽기]({selected_news.link})", unsafe_allow_html=True)

        if st.button("이 기사 요약하기"):
            with st.spinner("기사 본문을 가져와 AI로 요약 중입니다... 잠시만 기다려주세요."):
                article_text = get_article_text(selected_news.link, selected_feed_name)
                summary = summarize_text(article_text)
                
                st.subheader("🤖 AI 요약")
                st.write(summary)
