
import streamlit as st
import pandas as pd
import snowflake.connector

# Page config
st.set_page_config(page_title="Cortext Analyst", layout="centered")

# Heading
st.title("Cortext Analyst")
st.caption("Ask me anything about claims data.")

# ✅ Snowflake connection
def get_connection():
    return snowflake.connector.connect(
        user="kaunda",
        password="(Udiot@20251126)",
        account="ZEQWJME-NV17394",
        role="ACCOUNTADMIN",
        database="Cortext",
        schema="demo",
        warehouse="COMPUTE_WH"
    )

def run_query(query):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    finally:
        cur.close()
        conn.close()
    return df

# ✅ Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi Kaunda! Ask me about claims data."}
    ]

# Render previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your question here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ✅ Simple logic: detect keywords and build SQL
    bot_reply = ""
    if "total" in user_input.lower():
        query = """
        SELECT REGION, CLAIMSTATUS, SUM(CLAIMAMOUNT) AS TOTAL_AMOUNT
        FROM MASTERCLAIM
        GROUP BY REGION, CLAIMSTATUS
        ORDER BY TOTAL_AMOUNT DESC
        """
        df = run_query(query)
        if df.empty:
            bot_reply = "No data found for your query."
        else:
            bot_reply = "Here’s the summary:\n\n" + df.to_string(index=False)
    else:
        bot_reply = (
            "I'm connected to Snowflake. Try asking:\n"
            "- 'Show total claims by region'\n"
            "- 'Give me totals for North and Open claims'\n"
            "Natural language to SQL coming soon!"
        )

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
