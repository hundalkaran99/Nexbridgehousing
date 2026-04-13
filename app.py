import streamlit as st
import anthropic

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

PROVINCES = [
    "Select your province/territory",
    "Alberta", "British Columbia", "Manitoba", "New Brunswick",
    "Newfoundland and Labrador", "Northwest Territories", "Nova Scotia",
    "Nunavut", "Ontario", "Prince Edward Island", "Quebec",
    "Saskatchewan", "Yukon"
]

st.set_page_config(page_title="Nexbridge Housing", page_icon="🏠", layout="centered")

st.markdown("""
    <style>
    .header-box {
        background-color: #1a73e8;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .header-box h1 {
        color: white;
        font-size: 2rem;
        margin: 0;
    }
    .header-box p {
        color: #e8f0fe;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1>🏠 Nexbridge</h1>
        <p>Your Canadian housing guide — tenant rights, leases, renting & more</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    province = st.selectbox("", PROVINCES, label_visibility="collapsed")
with col2:
    if st.button("+ New Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask your housing question...")

if question:
    if province == "Select your province/territory":
        st.warning("Please select your province or territory first.")
    else:
        system_prompt = f"""You are a Canadian housing expert assistant called Nexbridge.
You help anyone in Canada with housing questions including tenants, landlords,
newcomers, and students. The user is located in {province}.

Always answer based on {province} housing laws and rules specifically.
Cover topics like renting, leases, tenant rights, deposits, evictions,
rent assistance, and buying property.

Speak in simple, clear English that anyone can understand.
Only answer housing-related questions. If someone asks about something else,
politely guide them back to housing topics."""

        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                answer = response.content[0].text
                st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
