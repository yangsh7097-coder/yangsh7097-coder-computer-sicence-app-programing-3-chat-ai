# [목적] 웹 애플리케이션 구축을 위한 Streamlit 라이브러리를 불러옵니다.
import streamlit as st
# [목적] Google의 거대 언어 모델(Gemini)을 사용하여 AI 챗봇 기능을 구현하기 위함입니다.
import google.generativeai as genai
# [목적] 데이터 처리 및 분석을 위해 Pandas를 사용합니다. (피드백 저장 시 활용)
import pandas as pd
from datetime import datetime
# [목적] 지도 기반의 인포그래픽 시각화를 위해 Plotly를 사용합니다.
import plotly.express as px
import os

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="인구 집중 데이터 탐정",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- 2. 커스텀 CSS 및 레이아웃 ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.markdown("""
<style>
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API 키 설정 ---
# secrets.toml 파일에 GEMINI_API_KEY = "내키" 형태로 저장되어 있어야 합니다.
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 GEMINI_API_KEY를 설정해주세요.")

# --- 4. 수업 내용 시스템 프롬프트 (AI 페르소나) ---
SYSTEM_INSTRUCTION = """
당신은 초등학교 5학년 사회 수업 '수도권 인구 집중의 원인' 탐구를 돕는 인공지능 도우미입니다.
아이들의 질문에 대해 다음 데이터를 바탕으로 '증거'를 제시하며 답변하세요.

[핵심 데이터 (2024년 교과서 기준)]
1. 면적과 인구: 수도권 면적은 국토의 11.8%이나, 인구는 약 50.7%가 집중됨.
2. 기업 수: 전국의 약 53%가 수도권에 집중되어 있음.
3. 의료 시설: 상급 종합병원 등 주요 의료 시설이 비수도권보다 월등히 많음.
4. 교육 시설: 주요 대학교와 공공기관이 수도권에 편중됨.
5. 문화 시설: 공연장, 도서관, 백화점 등 편의시설이 수도권에 집중됨.

[답변 원칙]
- 5학년 학생의 눈높이에 맞춰 아주 친절하게 설명하세요.
- 학생들이 "왜?"라고 물으면 "데이터를 보면 ~하기 때문이야"라고 인과관계를 설명하세요.
- 단순히 답을 주기보다 "그래프에서 어떤 차이가 보이니?"라고 되묻기도 하세요.
"""

# 모델 로드 함수 (시스템 프롬프트 적용)
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

def translate_role_for_gemini(role):
    return "model" if role == "assistant" else role

# --- 5. 피드백 저장 함수 ---
def save_feedback(message_index, rating, feedback_text=""):
    if message_index > 0:
        user_question = st.session_state.chat_log[message_index - 1]['content']
    else:
        user_question = "" 

    ai_answer = st.session_state.chat_log[message_index]['content']

    feedback_data = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "user_question": [user_question],
        "ai_answer": [ai_answer],
        "rating": [rating],
        "feedback_text": [feedback_text]
    }
    df = pd.DataFrame(feedback_data)

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feedback.csv")

    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(csv_path, mode='w', header=True, index=False, encoding='utf-8-sig')

# --- 6. 사이드바 UI ---
with st.sidebar:
    st.title("🕵️ 데이터 탐정 가이드")
    st.info("""
    **이렇게 질문해 보세요!**
    - "수도권에 기업이 얼마나 많아?"
    - "청년들이 왜 서울로 가려고 해?"
    - "병원이나 대학교는 어디에 더 많아?"
    - "수도권 땅은 좁은데 왜 사람이 많아?"
    """)
    
    st.markdown("---")
    st.subheader("🛠️ 탐구 도구")
    
    if st.button("처음부터 다시 탐구하기", use_container_width=True):
        st.session_state.chat_log = []
        st.rerun()

    # 대화 내용 다운로드
    if st.session_state.get("chat_log"):
        chat_history = "\n\n".join(
            f"**{m['role'].capitalize()}**: {m['content']}" 
            for m in st.session_state.chat_log
        )
        st.download_button(
            label="오늘의 탐구 기록 저장(TXT)",
            data=chat_history.encode('utf-8'),
            file_name="수도권_탐구기록.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- 7. 메인 화면 UI ---
st.title("🔍 인구 집중 데이터 탐정")
st.subheader("교과서 데이터를 바탕으로 인구 집중의 원인을 찾아보세요!")
st.info("📢 **주의사항:** 탐정 조수(AI)도 가끔 실수를 할 수 있어요! 데이터가 이상하면 교과서 85~87쪽을 꼭 확인해 보세요.")

# --- 7-1. 데이터 시각화 섹션 추가 ---
with st.expander("️ 우리나라 지역별 데이터 인포그래픽 (지도 탐색)", expanded=True):
    # 예시 데이터 (실제 통계청 데이터를 활용하면 더 좋습니다)
    regional_data = pd.DataFrame({
        "지역": ["서울", "경기", "인천", "부산", "대구", "광주", "대전"],
        "일자리(만 개)": [500, 450, 150, 120, 80, 60, 70],
        "상급 병원(개)": [14, 5, 3, 4, 5, 3, 1],
        "대학교(개)": [48, 35, 10, 22, 11, 17, 15],
        "대형 마트(개)": [65, 105, 27, 32, 20, 15, 14],
        "위도": [37.5665, 37.4138, 37.4563, 35.1796, 35.8714, 35.1595, 36.3504],
        "경도": [126.9780, 127.5183, 126.7052, 129.0756, 128.6014, 126.8526, 127.3845]
    })
    
    # 상단 요약 카드 (인포그래픽 느낌)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("수도권 기업 비중", "약 53%", "집중됨", delta_color="inverse")
    with col2:
        st.metric("수도권 인구 비중", "50.7%", "절반 이상", delta_color="inverse")
    with col3:
        st.metric("수도권 면적 비중", "11.8%", "매우 좁음")

    st.divider()

    selected_metric = st.selectbox("보고 싶은 데이터를 선택하세요", ["일자리(만 개)", "상급 병원(개)", "대학교(개)", "대형 마트(개)"])
    
    tab_map, tab_chart, tab_table = st.tabs(["🗺️ 우리나라 지도", "📉 막대 그래프", "📋 데이터 표"])
    
    with tab_map:
        # 지도 시각화 (인포그래픽 스타일)
        fig = px.scatter_mapbox(
            regional_data,
            lat="위도",
            lon="경도",
            size=selected_metric,
            color=selected_metric,
            color_continuous_scale="Reds",
            hover_name="지역",
            zoom=6,
            mapbox_style="carto-positron",
            height=500
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"▲ 원의 크기가 클수록 {selected_metric}가 많다는 뜻이에요! 주로 어느 쪽에 모여 있나요?")

    with tab_chart:
        # 지역별로 색상을 다르게 하여 시각화
        st.bar_chart(data=regional_data, x="지역", y=selected_metric, color="지역")

    with tab_table:
        # 아이들이 보기 좋게 아이콘과 함께 표시
        st.dataframe(
            regional_data,
            column_config={
                "일자리(만 개)": st.column_config.ProgressColumn("일자리", format="%d만", min_value=0, max_value=600),
                "상급 병원(개)": "🏥 병원 수",
                "대학교(개)": "🏫 대학교 수",
                "대형 마트(개)": "🛒 마트 수"
            },
            hide_index=True,
            use_container_width=True
        )

st.divider()

# --- 7-2. 채팅창 UI ---
chat_container = st.container(height=400)

with chat_container:
    # 초기 인사말 설정
    if "chat_log" not in st.session_state or len(st.session_state.chat_log) == 0:
        welcome_msg = "안녕! 나는 데이터 탐정 조수야. 🕵️\n\n교과서 86쪽의 그래프를 보다가 이해가 안 가는 수치가 있거나, **수도권에 왜 사람이 모이는지** 궁금한 점이 있으면 나에게 질문해 줘! 증거를 찾아줄게."
        st.session_state.chat_log = [{"role": "assistant", "content": welcome_msg}]

    # 대화 기록 및 피드백 버튼 출력
    for idx, message in enumerate(st.session_state.chat_log):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # AI 답변인 경우에만 좋아요/싫어요 버튼 표시
            if message["role"] == "assistant" and idx > 0:
                feedback_key_base = f"feedback_{idx}"
                col1, col2, _ = st.columns([1, 1, 8])
                with col1:
                    if st.button("👍", key=f"{feedback_key_base}_like"):
                        save_feedback(idx, "👍 좋았어요")
                        st.toast("탐구에 도움이 되었다니 다행이야! 😊")
                with col2:
                    if st.button("👎", key=f"{feedback_key_base}_dislike"):
                        st.session_state[f"show_feedback_input_{idx}"] = True
                
                # 아쉬워요 클릭 시 피드백 입력창 표시
                if st.session_state.get(f"show_feedback_input_{idx}"):
                    feedback_text = st.text_area("어떤 점이 아쉬웠나요?", key=f"{feedback_key_base}_text")
                    if st.button("피드백 보내기", key=f"{feedback_key_base}_submit"):
                        save_feedback(idx, "👎 아쉬워요", feedback_text)
                        st.toast("의견 고마워! 데이터를 더 꼼꼼히 확인할게. 🕵️")
                        st.session_state[f"show_feedback_input_{idx}"] = False

# --- 8. 챗봇 구동 (질문 입력 및 답변 생성) ---
if prompt := st.chat_input("수도권 데이터에 대해 질문해 보세요!"):
    # 사용자 질문 저장 및 출력
    st.session_state.chat_log.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # AI 답변 생성 및 출력
    with chat_container:
        with st.chat_message("assistant"):
            response_container = st.empty()
            
            try:
                # 모델 불러오기
                model = load_model()
                
                # 이전 대화 맥락 포함하여 API 형태에 맞게 변환
                gemini_messages = [
                    {"role": translate_role_for_gemini(m["role"]), "parts": [m["content"]]} 
                    for m in st.session_state.chat_log[:-1]  # 방금 넣은 user 질문 제외한 이전 기록
                ]
                
                # 챗 세션 시작 및 질문 전송
                chat = model.start_chat(history=gemini_messages)
                response = chat.send_message(prompt, stream=True)
                
                # 스트리밍 출력
                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        response_container.markdown(full_response)
                
                # 대화 기록에 최종 답변 저장
                st.session_state.chat_log.append({"role": "assistant", "content": full_response})
                st.rerun() # 피드백 버튼 생성을 위해 화면 새로고침

            except Exception as e:
                response_container.error(f"데이터를 분석하는 중 오류가 발생했습니다: {e}")
                st.session_state.chat_log.pop() # 에러 시 꼬임 방지를 위해 마지막 질문 제거