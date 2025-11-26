import streamlit as st
import google.generativeai as genai

st.write("안녕 나는 서울교대 앱프로그래밍 수업 전용 챗봇이야! 반가워! 무엇이든 물어봐!")

st.caption("단, 수업에서 다룬 내용만 답변할 수 있어요.")

# Configure Google Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to translate role from 'assistant' to 'model'
def translate_role_for_gemini(role):
    if role == "assistant":
        return "model"
    else:
        return role

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕 나는 서울교대 앱프로그래밍 수업 전용 챗봇이야! 반가워! 무엇이든 물어봐!"}]

for message in st.session_state.messages:
    # For Gemini, the "assistant" role is called "model"
    if message["role"] == "assistant":
        message["role"] = "model"
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("무엇이든 물어봐!"):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Prepare messages for Gemini API, translating roles
        gemini_messages = [
            {"role": translate_role_for_gemini(m["role"]), "parts": [m["content"]]}
            for m in st.session_state.messages
        ]

        # Call the Gemini API with streaming
        response = model.generate_content(gemini_messages, stream=True)

        for chunk in response:
            # Sometimes chunks can be empty, so we check for text
            if chunk.text:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌") # Typing effect
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "model", "content": full_response})
