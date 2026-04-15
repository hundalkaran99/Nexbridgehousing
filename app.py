import streamlit as st
import anthropic
from supabase import create_client
from tavily import TavilyClient
import resend
import json
import re

anthropic_client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

st.set_page_config(page_title="Cosmic AI", page_icon="✦", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #08090d; }
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
    .stMarkdown p { color: #c8cad8; }
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

def needs_search(question):
    search_keywords = [
        "today", "now", "current", "latest", "news", "weather",
        "price", "stock", "score", "recent", "2024", "2025", "2026",
        "what is happening", "right now", "this week", "tonight"
    ]
    return any(keyword in question.lower() for keyword in search_keywords)

def search_web(query):
    try:
        results = tavily.search(query=query, max_results=3)
        context = ""
        for r in results["results"]:
            context += f"Source: {r['url']}\n{r['content']}\n\n"
        return context
    except:
        return ""

def send_email(to_email, subject, body):
    try:
        params = {
            "from": "Cosmic AI <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "text": body
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        return False

def detect_email_intent(question):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    has_email = re.search(email_pattern, question)
    email_keywords = ["send email", "send an email", "email to", "write an email", "shoot an email"]
    has_keyword = any(keyword in question.lower() for keyword in email_keywords)
    return has_email and has_keyword

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In"):
            try:
                result = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = result.user
                st.session_state.messages = []
                st.rerun()
            except:
                st.error("Invalid email or password.")

    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({
                    "email": new_email,
                    "password": new_password
                })
                st.success("Account created! Please check your email to verify, then sign in.")
            except:
                st.error("Could not create account. Try a different email.")

else:
    user_id = st.session_state.user.id
    memory = get_memory(user_id)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("+ New"):
            st.session_state.messages = []
            st.rerun()
    with col3:
        if st.button("Sign Out"):
            supabase.auth.sign_out()
            st.session_state.user = None
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

        web_context = ""
        if needs_search(question):
            with st.spinner("Searching the web..."):
                web_context = search_web(question)

        email_sent = False
        if detect_email_intent(question):
            with st.spinner("Preparing email..."):
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                found_email = re.search(email_pattern, question)
                if found_email:
                    to_address = found_email.group()
                    email_response = anthropic_client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=500,
                        messages=[{
                            "role": "user",
                            "content": f"Write a short professional email based on this request: {question}. Reply with ONLY a JSON object with keys 'subject' and 'body'. Nothing else."
                        }]
                    )
                    try:
                        email_data = json.loads(email_response.content[0].text)
                        success = send_email(to_address, email_data["subject"], email_data["body"])
                        email_sent = success
                    except:
                        email_sent = False

        system_prompt = f"""You are Cosmic AI, a precise and intelligent personal assistant with access to real-time web search and email sending.

What you remember about this user:
{memory if memory else "Nothing yet — this is a new user."}

{f"Web search results for context:{chr(10)}{web_context}" if web_context else ""}

{"The email has been sent successfully." if email_sent else ""}

As you learn new important things about the user (name, location, job, preferences),
remember them. At the end of your response, if you learned something new and important,
add a line starting with 'REMEMBER:' followed by a brief note.

Answer every question clearly, accurately and concisely.
If you used web search results, mention that your answer is based on current web data.
If an email was sent, confirm it to the user."""

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
