from textblob import TextBlob

texts = [
    "The stock market is rising!",  # Expected: slight positive (~0.0 to 0.2)
    "This is fantastic news!",      # Expected: strong positive (> 0.5)
    "The situation is terrible.",   # Expected: negative (< 0)
]

for text in texts:
    print(f"Text: {text}")
    print("Sentiment Polarity:", TextBlob(text).sentiment.polarity)
    print("-" * 30)
