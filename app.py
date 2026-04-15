import streamlit as st
import anthropic

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

st.set_page_config(page_title="Cosmic AI", page_icon="✦", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #08090d;
    }
    
    .header-box {
        padding: 2.5rem 2rem 2rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1e2030;
    }
    
    .header-box h1 {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: 6px;
        text-transform: uppercase;
    }
    
    .header-box p {
        color: #4a5180;
        font-size: 0.78rem;
        margin-top: 0.6rem;
        margin-bottom: 0;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .stChatMessage {
        background: #0e0f1a !important;
        border: 1px solid #1e2030 !important;
        border-radius: 8px !important;
        padding: 0.8rem !important;
    }

    div.stButton > button {
        background: transparent;
        color: #4a5180;
        border: 1px solid #1e2030;
        border-radius: 6px;
        padding: 0.3rem 1rem;
        font-size: 0.78rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    div.stButton > button:hover {
        border-color: #4a5180;
        color: #ffffff;
        background: transparent;
    }

    section[data-testid="stChatInput"] {
        background: #0e0f1a !important;
        border: 1px solid #1e2030 !important;
        border-radius: 8px !important;
    }

    .stMarkdown p {
        color: #c8cad8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1>✦ Cosmic AI</h1>
        <p>Personal Intelligence System</p>
    </div>
""", unsafe_allow_html=True)

if st.button("+ New"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Message Cosmic AI...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system="You are Cosmic AI, a precise and intelligent personal assistant. Answer every question clearly, accurately and concisely.",
                messages=st.session_state.messages
            )
            answer = response.content[0].text
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
