
import streamlit as st
import pandas as pd
import snowflake.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Claims Dashboard", layout="wide")

st.title("Claims Analytics GenAI Dashboard")

# Snowflake connection
def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        database=os.getenv("SNOWFLAKE_DATABASE", "Cortext"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "demo"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
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

# -------------------------------
# Cortex Analyst Integration
# -------------------------------
st.subheader("Ask Cortex Analyst")
user_query = st.text_area("Ask a question about claims data:")
if st.button("Generate Insight"):
    cortex_sql = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE('{user_query}', 
    OBJECT_CONSTRUCT('data', (SELECT * FROM MASTERCLAIM LIMIT 100)));
    """
    try:
        result_df = run_query(cortex_sql)
        st.write("Cortex Response:")
        st.write(result_df)
    except Exception as e:
        st.error(f"Error running Cortex query: {e}")
