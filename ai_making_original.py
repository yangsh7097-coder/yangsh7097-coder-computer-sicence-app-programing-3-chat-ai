import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import os
import requests

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="AI Chatbot - 2025 Edition",
    page_icon="🤖",
    layout="centered", # 중앙 정렬 레이아웃
    initial_sidebar_state="auto"
)

# --- 2. 커스텀 CSS 주입 --- (style.css 파일 로드 및 인라인 CSS)
# style.css 파일을 로드하여 앱 전반에 걸쳐 모던한 다크 테마를 적용합니다.
def local_css(file_name):
    # 파일을 열기 전에 존재하는지 먼저 확인합니다.
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Warning: CSS file '{file_name}' not found. Styling might be incomplete.")

local_css("style.css")

# 기존 인라인 CSS 중 style.css에 없는 부분만 유지합니다.
st.markdown("""
<style>
    /* 메인 컨테이너의 최대 너비 조정 */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Configure Google Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 외부 도구(Tools) 정의 ---
def get_weather(city: str):
    """
    특정 도시의 현재 날씨 정보를 가져옵니다.
    """
    # 무료 날씨 API인 wttr.in 사용
    try:
        response = requests.get(f"https://wttr.in/{city}?format=j1")
        response.raise_for_status()
        weather_data = response.json()
        current_condition = weather_data['current_condition'][0]
        
        # 모델이 이해하기 쉬운 형태로 날씨 정보 요약
        return (
            f"{city}의 현재 날씨: "
            f"날씨 상태: {current_condition['weatherDesc'][0]['value']}, "
            f"온도: {current_condition['temp_C']}°C, "
            f"체감 온도: {current_condition['FeelsLikeC']}°C, "
            f"풍속: {current_condition['windspeedKmph']}km/h"
        )
    except Exception as e:
        return f"날씨 정보를 가져오는 데 실패했습니다: {e}"

# --- 성능 최적화를 위한 모델 캐싱 ---
@st.cache_resource
def load_model():
    """
    설명: AI 모델(GenerativeModel)은 로드하는 데 시간이 걸리는 무거운 객체입니다.
    @st.cache_resource 데코레이터는 이 함수가 앱 세션에서 딱 한 번만 실행되도록 보장합니다.
    이후 함수 호출 시에는 새로 모델을 로드하는 대신, 메모리에 저장된 기존 객체를 즉시 반환합니다.
    이점: 사용자가 메시지를 보낼 때마다 모델을 새로 로드하는 비효율을 없애고 앱의 반응 속도를 크게 향상시킵니다.
    """
    # 함수 호출 기능을 사용하기 위해 tools 매개변수와 함께 모델을 초기화합니다.
    model = genai.GenerativeModel(
        model_name='gemini-2.5-pro', tools=[get_weather])
    return model

# --- 피드백 저장을 위한 함수 ---
def save_feedback(message_index, rating, feedback_text=""):
    """
    사용자 피드백을 CSV 파일에 저장합니다.
    """
    # 피드백의 대상이 되는 사용자 질문과 AI 답변을 찾습니다.
    # AI 답변은 message_index에 있고, 사용자 질문은 그 바로 앞에 있습니다.
    if message_index > 0:
        user_question = st.session_state.messages[message_index - 1]['content']
    else:
        user_question = "" # 대화 시작 메시지에 대한 피드백일 경우

    ai_answer = st.session_state.messages[message_index]['content']

    feedback_data = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "user_question": [user_question],
        "ai_answer": [ai_answer],
        "rating": [rating],
        "feedback_text": [feedback_text]
    }
    df = pd.DataFrame(feedback_data)

    # 파일이 존재하면 기존 내용에 추가하고, 없으면 새로 만듭니다.
    if os.path.exists("feedback.csv"):
        df.to_csv("feedback.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df.to_csv("feedback.csv", mode='w', header=True, index=False, encoding='utf-8-sig')


# Function to translate role from 'assistant' to 'model'
def translate_role_for_gemini(role):
    if role == "assistant":
        return "model"
    else:
        return role

# --- 사이드바 구성 (UX 개선) ---
with st.sidebar:
    st.header("대화 관리")
    if st.button("새 대화 시작", use_container_width=True):
        st.session_state.messages = [] # 대화 기록 초기화
        st.rerun()
    
    # 대화 내용 다운로드 기능
    if st.session_state.get("messages"): # 메시지가 있을 때만 버튼 표시
        # 대화 기록을 하나의 텍스트로 변환
        chat_history = "\n\n".join(
            f"**{m['role'].capitalize()}**: {m['content']}" 
            for m in st.session_state.messages
        )
        st.download_button(
            label="대화 내용 다운로드",
            data=chat_history.encode('utf-8'),
            file_name="chatbot_history.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- 3. UI 레이아웃 구성 ---
st.title("🤖 AI Chatbot (2025 Edition)")
st.caption("서울교대 앱프로그래밍 수업 전용 챗봇")

# 대화 기록을 담을 컨테이너
chat_container = st.container(height=500)

with chat_container:
    if "messages" not in st.session_state:
        # Gemini API는 'assistant' 대신 'model' 역할을 사용합니다.
        st.session_state.messages = [{"role": "model", "content": "안녕하세요! 저는 2025년 11월 버전의 AI 챗봇입니다. 무엇이든 물어보세요."}]

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(translate_role_for_gemini(message["role"])):
            st.markdown(message["content"])

            # AI 답변(assistant 역할)에만 피드백 버튼 추가
            if message["role"] == "assistant":
                feedback_key_base = f"feedback_{idx}"
                
                col1, col2, _ = st.columns([1, 1, 8])
                with col1:
                    if st.button("👍", key=f"{feedback_key_base}_like"):
                        save_feedback(idx, "👍 좋았어요")
                        st.toast("피드백이 저장되었습니다. 감사합니다! 😊")
                with col2:
                    if st.button("👎", key=f"{feedback_key_base}_dislike"):
                        # '아쉬워요' 버튼을 누르면 피드백 입력창을 표시하기 위한 상태 저장
                        st.session_state[f"show_feedback_input_{idx}"] = True
                
                # '아쉬워요'가 선택된 경우, 텍스트 입력창 표시
                if st.session_state.get(f"show_feedback_input_{idx}"):
                    feedback_text = st.text_area("어떤 점이 아쉬웠는지 알려주실 수 있나요?", key=f"{feedback_key_base}_text")
                    if st.button("피드백 제출", key=f"{feedback_key_base}_submit"):
                        save_feedback(idx, "👎 아쉬워요", feedback_text)
                        st.toast("소중한 피드백이 저장되었습니다. 더 발전하는 AI가 되겠습니다! 🙇‍♂️")
                        # 제출 후 입력창 숨기기
                        st.session_state[f"show_feedback_input_{idx}"] = False
                        st.rerun()

# --- 4. 챗봇 로직 ---
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지를 기록하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # AI 응답을 생성하고 화면에 표시
    with chat_container:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # 캐시된 모델을 불러옵니다. 앱 실행 후 최초 한 번만 로드되고 이후에는 즉시 반환됩니다.
            model = load_model()

            gemini_messages = [
                {"role": translate_role_for_gemini(m["role"]), "parts": [m["content"]]}
                for m in st.session_state.messages
            ]

            # --- 실시간 타이핑 효과 및 함수 호출 로직 ---
            response_stream = model.generate_content(gemini_messages, stream=True)
            
            function_call_info = None
            
            # 1차 스트리밍: 텍스트를 출력하거나 함수 호출 정보를 찾습니다.
            for chunk in response_stream:
                # 모델이 함수 호출을 요청했는지 확인
                if (part := chunk.parts[0]).function_call:
                    function_call_info = part.function_call
                    break # 함수 호출이 감지되면 텍스트 출력을 멈춥니다.
                # 텍스트가 있으면 실시간으로 출력
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            # 함수 호출이 감지된 경우, 후속 처리를 합니다.
            if function_call_info:
                function_name = function_call_info.name
                if function_name == "get_weather":
                    city = function_call_info.args['city']
                    message_placeholder.markdown(f"`{city}`의 날씨를 검색 중입니다... 🛰️")
                    function_response = get_weather(city=city)

                    # 2차 스트리밍: 함수의 실행 결과를 모델에게 다시 전달하여 최종 답변을 실시간으로 받습니다.
                    final_response_stream = model.generate_content([
                        *gemini_messages,
                        response_stream.candidates[0].content, # 모델의 함수 호출 요청
                        {'role': 'tool', 'parts': [{'function_response': {'name': function_name, 'response': {'result': function_response}}}]}
                    ], stream=True)
                    
                    full_response = "" # 최종 답변을 위해 초기화
                    for chunk in final_response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response) # 최종 완성된 답변 표시
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun() # 채팅 입력 후 스크롤을 맨 아래로 유지하기 위해 새로고침