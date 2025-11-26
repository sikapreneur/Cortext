
import streamlit as st
import pandas as pd
import snowflake.connector
import os

# Load environment variables (optional if using .env)
from dotenv import load_dotenv
load_dotenv()

# Page config
st.set_page_config(page_title="Claims Dashboard", layout="wide")

st.title("Claims Analytics GenAI Dashboard")

# Snowflake connection
def get_connection():
    return snowflake.connector.connect(

        password="(Udiot@20251126)",
        account="ZEQWJME-NV17394",
        host = "ZEQWJME-NV17394.snowflakecomputing.com",
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

# Display results
st.subheader("Claims Summary")
st.dataframe(df)

# Chart
st.bar_chart(df.set_index("REGION")["TOTAL_AMOUNT"])
