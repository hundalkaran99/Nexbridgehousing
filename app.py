import streamlit as st
import anthropic

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

st.set_page_config(page_title="Cosmic AI", page_icon="🌌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1b3e 50%, #0a0a1a 100%);
    }
    
    .header-box {
        background: linear-gradient(135deg, #0d1b3e, #1a0a3e);
        border: 1px solid #3d4fdb;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 30px rgba(61, 79, 219, 0.3);
    }
    
    .header-box h1 {
        font-family: 'Orbitron', sans-serif;
        color: #a78bfa;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: 3px;
        text-shadow: 0 0 20px rgba(167, 139, 250, 0.5);
    }
    
    .header-box p {
        color: #7dd3fc;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
        letter-spacing: 1px;
    }

    .stChatMessage {
        background: rgba(13, 27, 62, 0.8) !important;
        border: 1px solid #1e3a6e !important;
        border-radius: 12px !important;
    }

    .stChatInput input {
        background: rgba(13, 27, 62, 0.9) !important;
        border: 1px solid #3d4fdb !important;
        color: white !important;
        border-radius: 12px !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #1a0a3e, #0d1b3e);
        color: #a78bfa;
        border: 1px solid #3d4fdb;
        border-radius: 8px;
        padding: 0.4rem 1rem;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #2a1a5e, #1d2b5e);
        color: #c4b5fd;
        border-color: #a78bfa;
    }

    .stSelectbox > div {
        background: rgba(13, 27, 62, 0.9) !important;
        border: 1px solid #3d4fdb !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1>🌌 COSMIC AI</h1>
        <p>✦ Your personal AI assistant from across the universe ✦</p>
    </div>
""", unsafe_allow_html=True)

if st.button("⭐ New Chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask the universe anything...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system="You are Cosmic AI, a helpful personal AI assistant. Answer any question clearly, helpfully and concisely.",
                messages=st.session_state.messages
            )
            answer = response.content[0].text
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
