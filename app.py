
import streamlit as st
import pandas as pd
import snowflake.connector

# Page config
st.set_page_config(page_title="Claims Dashboard", layout="wide")

st.title("Claims Analytics GenAI Dashboard")

# Snowflake connection
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

# Query function
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

# Sidebar filters
st.sidebar.header("Filters")
region_filter = st.sidebar.selectbox("Select Region", ["All", "North", "South", "East", "West"])
status_filter = st.sidebar.selectbox("Claim Status", ["All", "Open", "Closed", "Pending", "Rejected"])

# Build query dynamically (NOTE: uses simple string interpolation; be careful if exposing to user input)
base_query = """
SELECT REGION, CLAIMSTATUS, SUM(CLAIMAMOUNT) AS TOTAL_AMOUNT
FROM MASTERCLAIM
WHERE 1=1
"""
if region_filter != "All":
    base_query += f" AND REGION = '{region_filter}'"
if status_filter != "All":
    base_query += f" AND CLAIMSTATUS = '{status_filter}'"
base_query += " GROUP BY REGION, CLAIMSTATUS ORDER BY TOTAL_AMOUNT DESC"

# Run query
df = run_query(base_query)

# Display dashboard
st.subheader("Claims Summary")
st.dataframe(df, use_container_width=True)
if not df.empty and "REGION" in df.columns and "TOTAL_AMOUNT" in df.columns:
    st.bar_chart(df.set_index("REGION")["TOTAL_AMOUNT"])
else:
    st.info("No data available for the selected filters.")

# -------------------------------
# ✅ Chat Interface
# -------------------------------
st.subheader("Ask Cortext Analyst")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything about claims data."}
    ]

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your question...")
if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Very simple router: if user mentions summary, respond with current df
    if "summary" in user_input.lower() or "total" in user_input.lower():
        if df.empty:
            bot_reply = "I ran the current filters but didn’t find any data. Try different filters."
        else:
            bot_reply = "Here’s the current claims summary:\n\n" + df.to_markdown(index=False)
    else:
        bot_reply = (
            "I'm connected to Snowflake. You can ask things like:\n"
            "- 'Show total by region'\n"
            "- 'Give me totals for North and Open claims'\n"
            "I’ll add natural-language-to-SQL next."
        )

    # Show assistant reply (INDENTED inside the context manager)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
