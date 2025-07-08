import boto3
import json
import time
import requests
from textblob import TextBlob
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

API_KEY = "041e670e4e514a7094bcc521e551448a"
engine = create_engine("postgresql://postgres:awsadmin1234@newsdatabase.c1o4u2ksu2dq.eu-north-1.rds.amazonaws.com:5432/postgres")

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch news:", response.text)
        return "Failed"

    articles = response.json().get("articles", [])
    if not articles:
        print("No articles returned by API.")
        return "No Articles"

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
    print(df.head())

    try:
        df.to_sql("news_analytics", engine, if_exists="append", index=False)
        print("Data inserted successfully.")
    except Exception as e:
        print("Database insertion failed:", e)
        return "DB Error"

    with open("news_raw.json", "w") as f:
        json.dump(response.json(), f, indent=4)

    s3 = boto3.client("s3")
    s3.upload_file("news_raw.json", "news-raw-data-2025", f"news_raw_{int(time.time())}.json")

    print("Raw news data uploaded to S3 successfully.")
    return "Success"
