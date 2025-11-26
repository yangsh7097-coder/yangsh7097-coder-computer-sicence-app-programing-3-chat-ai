import streamlit as st

st.title("초등 교육 철학")

st.write("""
초등 교육 철학은 아이들이 건강하게 성장하고 발달할 수 있도록 돕는 교육의 기본 원리와 가치를 탐구합니다.
다양한 철학적 관점을 통해 교육의 목표, 방법, 내용에 대한 깊이 있는 이해를 제공합니다.
""")

st.header("주요 교육 철학")

# 교육 철학 목록
philosophies = {
    "자연주의": "자유로운 성장과 경험을 중시하며, 자연스러운 발달을 돕는 교육",
    "경험주의": "직접적인 경험을 통해 학습하고, 실생활에 적용 가능한 지식 습득을 강조",
    "구성주의": "학습자가 스스로 지식을 구성하고, 능동적인 참여를 유도하는 교육",
    "인본주의": "개인의 존엄성과 잠재력을 존중하며, 자아실현을 돕는 교육"
}

# 선택 상자
selected_philosophy = st.selectbox("철학을 선택하세요:", list(philosophies.keys()))

# 선택된 철학 설명 표시
st.subheader(selected_philosophy)
st.write(philosophies[selected_philosophy])

st.header("교육 철학자")

# 교육 철학자 목록 업데이트
philosophers = {
    "루소": "자연주의 교육 철학의 선구자. 아동 중심 교육 강조",
    "존 듀이": "경험주의 교육 철학의 대표자. 실용주의적 학습 강조",
    "피아제": "구성주의 교육 이론의 창시자. 인지 발달 단계 이론 제시",
    "마슬로": "인본주의 심리학자, 교육에 큰 영향. 자아실현 욕구 강조",
    "비고츠키": "사회문화적 인지 발달 이론. 사회적 상호작용의 중요성 강조",
    "파울로 프레이리": "비판적 교육학. 억압받는 자들의 교육 옹호"
}

# 선택 상자
selected_philosopher = st.selectbox("철학자를 선택하세요:", list(philosophers.keys()))

# 선택된 철학자 설명 표시
st.subheader(selected_philosopher)
st.write(philosophers[selected_philosopher])
