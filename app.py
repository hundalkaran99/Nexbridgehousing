import streamlit as st
import anthropic
from supabase import create_client

anthropic_client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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

def get_memory(user_id):
    try:
        result = supabase.table("memories").select("memory").eq("user_id", user_id).execute()
        if result.data:
            return result.data[0]["memory"]
        return ""
    except:
        return ""

def save_memory(user_id, memory):
    try:
        existing = supabase.table("memories").select("memory").eq("user_id", user_id).execute()
        if existing.data:
            supabase.table("memories").update({"memory": memory}).eq("user_id", user_id).execute()
        else:
            supabase.table("memories").insert({"user_id": user_id, "memory": memory}).execute()
    except:
        pass

if "user_id" not in st.session_state:
    st.session_state.user_id = st.text_input("Enter your name to get started:", key="name_input")
    if st.session_state.user_id:
        st.rerun()
    st.stop()

user_id = st.session_state.user_id
memory = get_memory(user_id)

col1, col2 = st.columns([3, 1])
with col2:
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

    system_prompt = f"""You are Cosmic AI, a precise and intelligent personal assistant.

What you remember about this user:
{memory if memory else "Nothing yet — this might be a new user."}

As you learn new important things about the user (name, location, job, preferences), 
remember them. At the end of your response, if you learned something new and important, 
add a line starting with 'REMEMBER:' followed by a brief note to update memory.

Answer every question clearly, accurately and concisely."""

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=st.session_state.messages
            )
            answer = response.content[0].text

            if "REMEMBER:" in answer:
                parts = answer.split("REMEMBER:")
                clean_answer = parts[0].strip()
                new_memory = parts[1].strip()
                updated_memory = memory + "\n" + new_memory if memory else new_memory
                save_memory(user_id, updated_memory)
                st.write(clean_answer)
            else:
                st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
