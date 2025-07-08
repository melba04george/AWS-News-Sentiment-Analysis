import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Database connection
engine = create_engine("postgresql://postgres:awsadmin1234@newsdatabase.c1o4u2ksu2dq.eu-north-1.rds.amazonaws.com:5432/postgres")

st.set_page_config(page_title="News Analytics Sentiment Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.title("View News")
page = st.sidebar.radio("Navigation", ["View News", "Analytics"])

# Explanation section
st.sidebar.header("Explanation")
st.sidebar.write("""
Sentiment score indicates a positive sentiment when the score is positive and conversely, when the score is negative the sentiment is also negative.

**Scores above 0.2 = very positive (green), below -0.2 = very negative (red), between -0.2 and 0.2 = neutral (grey)**

Adjust starting date or ending date to refresh data
""")

st.title("News Analytics Sentiment Score Dashboard")

@st.cache_data
def get_data():
    query = "SELECT * FROM news_analytics ORDER BY timestamp DESC LIMIT 100"
    return pd.read_sql(query, engine)

# Load data
df = get_data()

# Clean timestamp column
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])

# Row-wise coloring function
def color_rows(row):
    if row['sentiment_score'] > 0.2:
        return ['background-color: lightgreen'] * len(row)
    elif row['sentiment_score'] < -0.2:
        return ['background-color: lightcoral'] * len(row)
    else:
        return ['background-color: lightgrey'] * len(row)

# View News Page
if page == "View News":
    st.write(f"Last update date : {df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')}")
    styled_df = df.style.apply(color_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)

# Analytics Page
elif page == "Analytics":
    unique_dates = df['timestamp'].dt.date.unique()
    selected_date = st.selectbox("Select date", sorted(unique_dates, reverse=True))

    filtered_df = df[df['timestamp'].dt.date == selected_date]

    if filtered_df.empty:
        st.warning("No data available for selected date.")
    else:
        st.dataframe(filtered_df)

        fig = px.line(filtered_df, x='timestamp', y='sentiment_score', title='Sentiment Score Over Time')
        st.plotly_chart(fig, use_container_width=True)
