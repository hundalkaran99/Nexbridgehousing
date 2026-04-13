import streamlit as st
import anthropic

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are a Canadian housing expert assistant called Nexbridge. 
You help anyone in Canada with housing questions including tenants, landlords, 
newcomers, and students. You answer questions about renting, leases, tenant rights, 
deposits, evictions, rent assistance, and buying property in Canada.

Always mention which province the rules apply to when relevant, since housing laws 
differ by province. Speak in simple, clear English that anyone can understand. 
If you don't know someone's province, ask them first before answering.

Only answer housing-related questions. If someone asks about something else, 
politely guide them back to housing topics."""

st.set_page_config(page_title="Nexbridge", page_icon="🏠")
st.title("Nexbridge 🏠")
st.write("Your Canadian housing guide. Ask me anything about renting, tenant rights, leases, and more.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("+ New Chat"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask your housing question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=st.session_state.messages
    )

    answer = response.content[0].text
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
