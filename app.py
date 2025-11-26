
import streamlit as st

# Page config
st.set_page_config(page_title="Cortext Analyst", layout="centered")

# Heading
st.title("Cliam Analytic AI Dashboard")
st.caption("Ask me anything about claims data.")

# ✅ Chat Interface Only
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi Kaunda! How can I help you today?"}
    ]

# Render previous messages (optional, can remove for ultra-clean look)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Big chat input (Google-like experience)
user_input = st.chat_input("Type your question here...")
if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Simple placeholder response
    bot_reply = (
        "I'm ready to help! Soon I'll connect to Snowflake and answer with real data.\n"
        "For now, I just echo: " + user_input
    )

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
