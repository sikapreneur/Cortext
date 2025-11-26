
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
    cur.execute(query)
    df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.close()
    conn.close()
    return df

# Sidebar filters
st.sidebar.header("Filters")
region_filter = st.sidebar.selectbox("Select Region", ["All", "North", "South", "East", "West"])
status_filter = st.sidebar.selectbox("Claim Status", ["All", "Open", "Closed", "Pending", "Rejected"])

# Build query dynamically
query = "SELECT REGION, CLAIMSTATUS, SUM(CLAIMAMOUNT) AS TOTAL_AMOUNT FROM MASTERCLAIM WHERE 1=1"
if region_filter != "All":
    query += f" AND REGION = '{region_filter}'"
if status_filter != "All":
    query += f" AND CLAIMSTATUS = '{status_filter}'"
query += " GROUP BY REGION, CLAIMSTATUS ORDER BY TOTAL_AMOUNT DESC"

# Run query
df = run_query(query)

# Display dashboard
st.subheader("Claims Summary")
st.dataframe(df)
st.bar_chart(df.set_index("REGION")["TOTAL_AMOUNT"])

# -------------------------------
# ✅ Chat Interface
# -------------------------------
st.subheader("Ask Cortext Analyst")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi Kaunda! Ask me anything about claims data."}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Simple logic: if user asks for data, run query dynamically
    if "total claims" in user_input.lower():
        bot_reply = f"Here is the summary:\n\n{df.to_markdown()}"
    else:
        bot_reply = "I'm connected to Snowflake. Soon I'll answer with AI-powered insights!"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
