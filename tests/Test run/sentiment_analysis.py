import requests
import pandas as pd
from transformers import pipeline

NEWS_API_KEY = 'your_newscatcher_api_key'
NEWS_API_URL = 'https://api.newscatcherapi.com/v2/search'

def fetch_news_articles():
    headers = {'x-api-key': NEWS_API_KEY}
    params = {'q': 'oil demand Sri Lanka', 'lang': 'en', 'sort_by': 'relevancy', 'page_size': 50}
    response = requests.get(NEWS_API_URL, headers=headers, params=params)
    articles = response.json().get('articles', [])
    return [article['title'] for article in articles]

# Load sentiment analysis model
sentiment_analyzer = pipeline('sentiment-analysis', model='ProsusAI/finbert')

def analyze_sentiments(titles):
    return sentiment_analyzer(titles)

if __name__ == "__main__":
    news_titles = fetch_news_articles()
    news_sentiments = analyze_sentiments(news_titles)

    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    sentiment_scores = [sentiment_map[sent['label']] for sent in news_sentiments]

    sentiment_df = pd.DataFrame({
        'date': pd.to_datetime('today').normalize(),
        'sentiment_score': [sum(sentiment_scores) / len(sentiment_scores)]
    })

    sentiment_df.to_csv("sentiment_data.csv", index=False)
    print("Sentiment analysis completed!")
