from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

song_lyrics = "I'm feeling good, everything is great!"

sentiment_score = analyzer.polarity_scores(song_lyrics)

if sentiment_score['compound'] > 0.2:
    mood = "happy"
elif sentiment_score['compound'] < -0.2:
    mood = "sad"
else:
    mood = "neutral"

print(f"Sentiment score: {sentiment_score}")
print(f"Mood classification: {mood}")


def analyze_sentiment(text):
    if not text:
        return "No input text provided."
    if "happy" in text.lower():
        sentiment = "positive"
    elif "sad" in text.lower():
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return f"Detected sentiment: {sentiment}"
