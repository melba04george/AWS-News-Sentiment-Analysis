import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob
from datetime import datetime
import boto3
import json
import time
from sqlalchemy import create_engine

# AWS S3 Credentials - Use IAM Role for ECS, no hardcoding here

# Database Connection
engine = create_engine("postgresql://postgres:awsadmin1234@newsdatabase.c1o4u2ksu2dq.eu-north-1.rds.amazonaws.com:5432/postgres")

# Function to fetch news & store
def fetch_news():
    API_KEY = "041e670e4e514a7094bcc521e551448a"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch news")
        return pd.DataFrame()

    articles = response.json().get("articles", [])
    if not articles:
        st.warning("No articles found.")
        return pd.DataFrame()

    data = []
    for article in articles:
        title = article.get("title", "")
        author = article.get("author", "Unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sentiment = TextBlob(title).sentiment.polarity

        data.append({
            "author": author,
            "description": title,
            "sentiment_score": sentiment,
            "timestamp": timestamp
        })

    df = pd.DataFrame(data)

    # Insert into Database
    try:
        df.to_sql("news_analytics", engine, if_exists="append", index=False)
        # st.success("Data inserted into database.")
    except Exception as e:
        st.error(f"Database insertion failed: {e}")

    # Upload raw JSON to S3
    with open("news_raw.json", "w") as f:
        json.dump(response.json(), f, indent=4)

    s3 = boto3.client("s3")
    try:
        s3.upload_file("news_raw.json", "news-raw-data-2025", f"news_raw_{int(time.time())}.json")
        # st.success("Raw news data uploaded to S3.")
    except Exception as e:
        st.error(f"S3 upload failed: {e}")

    return df


# ✅ Streamlit App
st.title("Live News Dashboard")

if st.button("Fetch Latest News"):
    st.info("Fetching latest news...")
    df = fetch_news()
    if not df.empty:
        st.dataframe(df)

# Auto-refresh every 60 seconds
st_autorefresh = st.empty()

