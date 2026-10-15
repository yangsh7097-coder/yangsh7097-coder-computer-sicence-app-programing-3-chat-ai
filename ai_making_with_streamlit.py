# ======================================================
# 🔍 수도권 인구 집중 탐구 AI 도우미
# 5학년 2반 사회 수업 - 수도권 인구 집중의 원인 (11/16차시)
# 교수·학습 모형: 탐구학습 (직소 수업 기법 활용)
# ======================================================

import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="인구 집중 데이터 탐정",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. 커스텀 CSS ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.markdown("""
<style>
    .main .block-container {
        max-width: 850px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .activity-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 100%);
        border: 1px solid #2d6a9f;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
    }
    .hypothesis-box {
        background-color: #1a2e1a;
        border-left: 4px solid #4caf50;
        border-radius: 6px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
    }
    .data-badge {
        background-color: #2d4a22;
        border: 1px solid #4caf50;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API 키 설정 ---
# secrets.toml에 GOOGLE_API_KEY 또는 GEMINI_API_KEY로 저장
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ `.streamlit/secrets.toml`에 `GOOGLE_API_KEY = '여러분의키'` 를 설정해주세요.")
    st.stop()

# --- 4. 수업 시스템 프롬프트 (수업 지도안 전체 반영) ---
SYSTEM_INSTRUCTION = """
당신은 초등학교 5학년 2반 사회 수업 '수도권 인구 집중의 원인 탐구'를 도와주는 AI 조수입니다.
이 수업은 탐구학습 모형과 직소 수업 기법을 활용하여 진행됩니다.

[수업 기본 정보]
- 단원: 2. 우리나라 지역 탐구
- 차시: 수도권 인구 집중의 원인 알아보기 (11/16차시)
- 탐구 질문: 수도권 인구 집중의 원인은 무엇일까?
- 학습 목표: 수도권 인구 집중의 원인을 알아보고 설명할 수 있다.
- 교과 역량: 비판적 사고 역량, 정보 활용 능력 역량

[수업 흐름 - 탐구학습 모형]
1단계 문제 제기: A지역(촌락, 월급 높지만 편의시설 없음) vs B지역(도시, 인프라 풍부) 선택하기
2단계 가설 설정 (활동1): "수도권에 일자리·교육·문화시설이 비수도권보다 많기 때문에 인구가 집중될 것이다"
3단계 자료 수집·분석 (활동2): 직소 기법 - 모둠별로 기업/병원/대학교/문화시설 통계 자료 찾아 분석
4단계 탐구 결과 정리 (활동3): 가설 검증 및 최종 결론 도출
5단계 정리: 핵심 내용 복습 + 후속 차시(지역 불균형) 예고

[핵심 데이터 - 수도권 집중 현황]
1. 면적과 인구: 수도권 면적은 국토의 11.8%이나, 인구는 약 50.7%가 집중됨
2. 기업 수: 전국 기업의 약 53%가 수도권(서울·경기·인천)에 집중
3. 의료 시설: 상급 종합병원 43개 중 24개(56%)가 수도권 위치
4. 대학교: 서울 소재 대학 48개, 경기 35개, 인천 10개 - 합계 93개(전국의 약 35%)
5. 문화 시설: 공연장, 전시관, 백화점 등 생활편의시설 수도권 집중

[직소 모둠 주제]
- 1모둠: 기업 수 비교 (수도권 vs 비수도권)
- 2모둠: 병원(의료시설) 수 비교
- 3모둠: 대학교 수 비교
- 4모둠: 문화·편의시설 수 비교

[답변 원칙]
- 5학년 학생의 눈높이에 맞춰 친절하고 쉽게 설명하세요
- 데이터와 그래프를 근거로 "이 수치를 보면 ~하기 때문이야"라고 설명하세요
- 단순히 답을 주기보다 "그래프에서 어떤 차이가 보이니?" 처럼 되묻기도 하세요
- 학생이 스스로 결론을 내릴 수 있도록 도와주세요
- 수도권 집중이 단순히 "좋아서"가 아닌, 사회·경제적 인프라 편중 때문임을 유도하세요
- 후속 학습(지역 불균형 문제)과 연결 지어 생각해보게 도와주세요
- 이모지를 적절히 활용해 친근하게 답변하세요
"""

# --- 5. 모델 로드 ---
@st.cache_resource
def load_model():
    # 최신 지원 모델인 gemini-3.8-flash 사용 (필요시 gemini-flash-latest로 fallback)
    for model_name in ["gemini-3.8-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
        try:
            return genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_INSTRUCTION
            )
        except Exception:
            continue
    return genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

def translate_role_for_gemini(role):
    return "model" if role == "assistant" else role

# --- 6. 피드백 저장 ---
def save_feedback(message_index, rating, feedback_text=""):
    user_question = st.session_state.chat_log[message_index - 1]['content'] if message_index > 0 else ""
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

# --- 7. 사이드바 ---
with st.sidebar:
    st.title("🕵️ 탐정 안내판")
    
    # 수업 정보
    with st.expander("📋 오늘의 수업 정보", expanded=True):
        st.markdown("""
        - **단원**: 2. 우리나라 지역 탐구  
        - **차시**: 11/16차시  
        - **탐구 질문**: 수도권 인구 집중의 원인은 무엇일까?  
        - **모형**: 탐구학습 (직소 기법)
        """)

    st.markdown("---")
    
    # 활동 단계 안내
    st.subheader("📍 탐구 활동 단계")
    st.markdown("""
    <div class="activity-card">
    <b>🔵 [활동1]</b> 우리의 짐작 확인하기<br>
    <small>→ 가설 세우기</small>
    </div>
    <div class="activity-card">
    <b>🟡 [활동2]</b> 데이터 속 증거 찾기<br>
    <small>→ 직소 모둠 자료 분석</small>
    </div>
    <div class="activity-card">
    <b>🟢 [활동3]</b> 탐구 결과 정리하기<br>
    <small>→ 가설 검증 & 결론 도출</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 질문 예시
    st.subheader("💡 이렇게 질문해봐요!")
    st.info("""
    - "수도권에 기업이 얼마나 많아?"
    - "왜 청년들이 서울로 가려고 해?"
    - "병원이나 대학교는 어디에 더 많아?"
    - "수도권 땅은 좁은데 왜 사람이 많아?"
    - "지방에 사람이 줄면 어떤 문제가 생겨?"
    """)
    
    st.markdown("---")
    
    # 탐구 도구
    st.subheader("🛠️ 탐구 도구")
    if st.button("🔄 처음부터 다시 탐구하기", use_container_width=True):
        st.session_state.chat_log = []
        st.session_state.hypothesis = ""
        st.session_state.activity_step = 0
        st.rerun()

    if st.session_state.get("chat_log"):
        chat_history = "\n\n".join(
            f"{'학생' if m['role'] == 'user' else 'AI 조수'}: {m['content']}"
            for m in st.session_state.chat_log
        )
        st.download_button(
            label="📥 오늘의 탐구 기록 저장",
            data=chat_history.encode('utf-8'),
            file_name=f"수도권탐구기록_{datetime.now().strftime('%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- 8. 메인 화면 ---
st.title("🔍 인구 집중 데이터 탐정")
st.markdown("#### 🗺️ 수도권 인구 집중의 원인을 데이터로 찾아봐요!")
st.info("💡 **탐정 조수(AI)도 가끔 실수를 해요!** 이상한 내용이 있으면 교과서 85~87쪽을 확인하고 선생님께 알려주세요.")

# --- 9. 데이터 인포그래픽 섹션 ---
with st.expander("📊 우리나라 지역별 인프라 현황 (클릭해서 탐색하기)", expanded=True):
    
    # 핵심 통계 요약 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏢 수도권 기업 비중", "약 53%", "비수도권보다 많음", delta_color="inverse")
    with col2:
        st.metric("👥 수도권 인구 비중", "50.7%", "절반 이상 거주", delta_color="inverse")
    with col3:
        st.metric("🗺️ 수도권 면적 비중", "11.8%", "전국의 8분의 1", delta_color="normal")

    st.divider()
    
    # 지역별 상세 데이터
    regional_data = pd.DataFrame({
        "지역": ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산"],
        "일자리(만 개)": [500, 450, 150, 120, 80, 60, 70, 55],
        "상급 병원(개)": [14, 7, 3, 4, 5, 3, 1, 1],
        "대학교(개)": [48, 35, 10, 22, 11, 17, 15, 5],
        "대형 마트(개)": [65, 105, 27, 32, 20, 15, 14, 10],
        "인구(만 명)": [940, 1360, 297, 330, 241, 144, 148, 112],
        "위도": [37.5665, 37.4138, 37.4563, 35.1796, 35.8714, 35.1595, 36.3504, 35.5384],
        "경도": [126.9780, 127.5183, 126.7052, 129.0756, 128.6014, 126.8526, 127.3845, 129.3114]
    })

    selected_metric = st.selectbox(
        "📌 살펴볼 데이터를 선택하세요",
        ["일자리(만 개)", "상급 병원(개)", "대학교(개)", "대형 마트(개)", "인구(만 명)"],
        help="직소 모둠별로 각자의 주제를 선택해서 분석해보세요!"
    )

    tab_map, tab_bar, tab_compare, tab_table = st.tabs(["🗺️ 지도", "📊 막대그래프", "⚖️ 수도권 vs 비수도권", "📋 데이터 표"])

    with tab_map:
        fig = px.scatter_map(
            regional_data,
            lat="위도", lon="경도",
            size=selected_metric,
            color=selected_metric,
            color_continuous_scale="RdYlGn_r",
            hover_name="지역",
            hover_data={"위도": False, "경도": False, selected_metric: True},
            zoom=6,
            map_style="carto-positron",
            height=450,
            title=f"지역별 {selected_metric} 분포"
        )
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"🔴 원이 클수록 {selected_metric}가 많아요! 주로 어느 쪽에 집중되어 있나요?")

    with tab_bar:
        # 수도권 강조 색상
        colors = ["#e74c3c" if r in ["서울", "경기", "인천"] else "#3498db" for r in regional_data["지역"]]
        fig2 = go.Figure(go.Bar(
            x=regional_data["지역"],
            y=regional_data[selected_metric],
            marker_color=colors,
            text=regional_data[selected_metric],
            textposition='outside'
        ))
        fig2.update_layout(
            title=f"지역별 {selected_metric} 비교 (🔴수도권 / 🔵비수도권)",
            xaxis_title="지역",
            yaxis_title=selected_metric,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=380
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab_compare:
        # 수도권 vs 비수도권 파이 차트
        capital = regional_data[regional_data["지역"].isin(["서울", "경기", "인천"])][selected_metric].sum()
        non_capital = regional_data[~regional_data["지역"].isin(["서울", "경기", "인천"])][selected_metric].sum()
        # 비수도권 전체 추정 (표시된 도시 외 지역 포함 비율 보정)
        non_capital_est = non_capital * 2.5  # 표에 없는 비수도권 지역 감안
        
        fig3 = go.Figure(go.Pie(
            labels=["🔴 수도권 (서울·경기·인천)", "🔵 비수도권 (나머지 전국)"],
            values=[capital, non_capital_est],
            hole=0.4,
            marker_colors=["#e74c3c", "#3498db"]
        ))
        fig3.update_layout(
            title=f"{selected_metric} - 수도권 vs 비수도권 비율",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=380
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("⚠️ 비수도권 수치는 주요 도시 기준 추정값입니다. 실제 통계는 통계청(kosis.kr)에서 확인하세요!")

    with tab_table:
        st.dataframe(
            regional_data.drop(columns=["위도", "경도"]),
            column_config={
                "지역": "🏙️ 지역",
                "일자리(만 개)": st.column_config.ProgressColumn("💼 일자리", format="%d만개", min_value=0, max_value=600),
                "상급 병원(개)": st.column_config.NumberColumn("🏥 상급병원", format="%d개"),
                "대학교(개)": st.column_config.NumberColumn("🏫 대학교", format="%d개"),
                "대형 마트(개)": st.column_config.NumberColumn("🛒 대형마트", format="%d개"),
                "인구(만 명)": st.column_config.ProgressColumn("👥 인구", format="%d만명", min_value=0, max_value=1400),
            },
            hide_index=True,
            use_container_width=True
        )

# --- 10. 가설 작성 섹션 (활동1) ---
st.divider()
with st.expander("📝 [활동1] 나의 가설 작성하기 (우리의 짐작 확인하기)", expanded=False):
    st.markdown("""
    <div class='hypothesis-box'>
    💭 <b>탐구 질문:</b> 수도권 인구 집중의 원인은 무엇일까?<br>
    아래에 여러분의 짐작(가설)을 써보세요!
    </div>
    """, unsafe_allow_html=True)
    
    hypothesis_example = "수도권에 _________ 이/가 비수도권보다 많기 때문에 인구가 집중될 것이다."
    if "hypothesis" not in st.session_state:
        st.session_state.hypothesis = ""
    
    hypothesis_input = st.text_area(
        "✏️ 나의 가설:",
        value=st.session_state.hypothesis,
        placeholder=hypothesis_example,
        height=100,
        help="데이터를 보기 전에 먼저 내 생각을 써봐요!"
    )
    
    col_h1, col_h2 = st.columns([1, 3])
    with col_h1:
        if st.button("💾 가설 저장", use_container_width=True):
            st.session_state.hypothesis = hypothesis_input
            st.success("✅ 가설이 저장되었어요! 활동2를 통해 확인해봐요.")
    
    if st.session_state.get("hypothesis"):
        st.markdown(f"""
        <div class='hypothesis-box'>
        📌 <b>내가 세운 가설:</b> "{st.session_state.hypothesis}"
        </div>
        """, unsafe_allow_html=True)

# --- 11. 직소 모둠 활동 안내 (활동2) ---
with st.expander("👥 [활동2] 직소 모둠 탐구 안내 (데이터 속 증거 찾기)", expanded=False):
    st.markdown("#### 우리 모둠은 어떤 주제를 조사하나요?")
    
    team_cols = st.columns(4)
    team_topics = [
        {"num": "1모둠", "icon": "🏢", "topic": "기업 수 비교", "keyword": "전국 기업 수", "hint": "수도권에 대기업, 중소기업이 얼마나 있는지 찾아봐요"},
        {"num": "2모둠", "icon": "🏥", "topic": "병원 수 비교", "keyword": "상급종합병원 지역별", "hint": "큰 병원이 어느 지역에 더 많은지 찾아봐요"},
        {"num": "3모둠", "icon": "🏫", "topic": "대학교 수 비교", "keyword": "지역별 대학교 수", "hint": "대학교가 서울에 얼마나 집중되어 있는지 찾아봐요"},
        {"num": "4모둠", "icon": "🎭", "topic": "문화·편의시설 비교", "keyword": "수도권 문화시설", "hint": "공연장, 백화점 등이 어디에 더 많은지 찾아봐요"},
    ]
    
    for i, team in enumerate(team_topics):
        with team_cols[i]:
            st.markdown(f"""
            <div class='activity-card' style='text-align:center;'>
            <b>{team['icon']} {team['num']}</b><br>
            <b>{team['topic']}</b><br>
            <small style='color:#aaa;'>{team['hint']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 📊 디벗(태블릿)에서 찾아볼 검색어 추천")
    st.markdown("""
    - 🔍 **통계청 국가통계포털**: [kosis.kr](https://kosis.kr) → "지역별 사업체 수"
    - 🔍 **보건복지부**: "상급 종합병원 현황"
    - 🔍 **대학알리미**: [academyinfo.go.kr](https://www.academyinfo.go.kr) → "지역별 대학 수"
    """)

st.divider()

# --- 12. AI 챗봇 섹션 ---
st.subheader("🤖 AI 탐정 조수에게 질문하기")
st.caption("데이터를 보다가 궁금한 점이 있으면 뭐든 물어봐요!")

chat_container = st.container(height=420)

# 초기 인사말
if "chat_log" not in st.session_state or len(st.session_state.chat_log) == 0:
    welcome_msg = """안녕! 나는 데이터 탐정 조수야 🕵️

오늘 우리는 **수도권 인구 집중의 원인**을 데이터로 찾아볼 거야!

📌 위의 그래프를 살펴보고 이런 것들을 질문해봐:
- "서울에 병원이 얼마나 많아?"
- "왜 사람들이 수도권으로 이사 가려고 해?"
- "지방에 사람이 줄어들면 무슨 일이 생겨?"

자, 어떤 게 궁금해? 🔍"""
    st.session_state.chat_log = [{"role": "assistant", "content": welcome_msg}]

with chat_container:
    for idx, message in enumerate(st.session_state.chat_log):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
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

                if st.session_state.get(f"show_feedback_input_{idx}"):
                    feedback_text = st.text_area("어떤 점이 아쉬웠나요?", key=f"{feedback_key_base}_text")
                    if st.button("피드백 보내기", key=f"{feedback_key_base}_submit"):
                        save_feedback(idx, "👎 아쉬워요", feedback_text)
                        st.toast("의견 고마워! 더 열심히 도와줄게. 🕵️")
                        st.session_state[f"show_feedback_input_{idx}"] = False

# --- 13. 챗봇 구동 ---
if prompt := st.chat_input("수도권 데이터에 대해 질문해 보세요!"):
    st.session_state.chat_log.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    with chat_container:
        with st.chat_message("assistant"):
            response_container = st.empty()
            try:
                model = load_model()
                gemini_messages = [
                    {"role": translate_role_for_gemini(m["role"]), "parts": [m["content"]]}
                    for m in st.session_state.chat_log[:-1]
                ]
                chat = model.start_chat(history=gemini_messages)
                response = chat.send_message(prompt, stream=True)

                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)

                st.session_state.chat_log.append({"role": "assistant", "content": full_response})
                st.rerun()

            except Exception as e:
                response_container.error(f"오류가 발생했습니다: {e}\n\n잠시 후 다시 시도해보거나 선생님께 알려주세요.")
                if st.session_state.chat_log and st.session_state.chat_log[-1]["role"] == "user":
                    st.session_state.chat_log.pop()

# --- 14. 하단 결론 정리 섹션 (활동3) ---
st.divider()
with st.expander("✅ [활동3] 탐구 결론 정리하기", expanded=False):
    st.markdown("#### 데이터 탐구를 통해 알게 된 것을 정리해봐요!")
    
    conclusion_input = st.text_area(
        "💬 오늘 탐구로 알게 된 수도권 인구 집중의 원인:",
        placeholder="수도권에 _________이/가 집중되어 있기 때문에 인구가 모여듭니다.",
        height=120
    )
    
    if st.button("📤 결론 AI에게 확인받기", use_container_width=False):
        if conclusion_input.strip():
            check_prompt = f"학생이 오늘 탐구 결론을 이렇게 정리했어: '{conclusion_input}'. 이 결론이 데이터 증거와 잘 맞는지 친절하게 피드백해줘. 잘 된 부분은 칭찬하고, 보완할 점이 있으면 힌트를 줘."
            st.session_state.chat_log.append({"role": "user", "content": f"[결론 확인 요청] {conclusion_input}"})
            st.rerun()
        else:
            st.warning("결론을 먼저 작성해주세요!")
    
    st.markdown("---")
    st.markdown("#### 🧠 다음 시간 예고")
    st.markdown("""
    > 💭 **생각해봐요**: 만약 우리나라 사람의 90%가 수도권에 산다면 어떤 일이 벌어질까요?  
    > 다음 시간에는 **인구 집중으로 인한 문제와 해결 방안**을 알아볼 거예요!
    """)