import httpx
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_URL = "https://newsapi.org/v2/everything"

TICKER_QUERIES = {
    # US Stocks
    "AAPL":     "Apple Inc stock",
    "TSLA":     "Tesla stock",
    "GOOGL":    "Alphabet Google stock",
    "NVDA":     "NVIDIA stock",
    "MSFT":     "Microsoft stock",
    "AMZN":     "Amazon stock",
    "META":     "Meta Facebook stock",
    "NFLX":     "Netflix stock",
    "IBM":      "IBM stock",
    # Indian Stocks
    "INFY":     "Infosys stock",
    "TCS":      "Tata Consultancy Services stock",
    "RELIANCE": "Reliance Industries stock",
    "HDFCBANK": "HDFC Bank stock",
    "WIPRO":    "Wipro stock",
    "ZOMATO":   "Zomato stock",
    "PAYTM":    "Paytm One97 Communications stock",
    "IRCTC":    "IRCTC stock India",
}

TRUSTED_DOMAINS = (
    "reuters.com,bloomberg.com,cnbc.com,wsj.com,ft.com,"
    "economictimes.indiatimes.com,livemint.com,"
    "moneycontrol.com,businessstandard.com"
)

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove common HTML artifacts
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("<br>", " ")
    text = text.replace("</br>", " ")
    return text.strip()

async def fetch_news_for_ticker(ticker: str) -> list:
    query = TICKER_QUERIES.get(ticker, f"{ticker} stock market")

    params = {
        "q":        query,
        "sortBy":   "publishedAt",
        "pageSize": 20,
        "language": "en",
        "domains":  TRUSTED_DOMAINS,
        "apiKey":   os.getenv("NEWS_API_KEY")
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

    raw_articles = data.get("articles", [])

    cleaned_articles = []
    for article in raw_articles:
        title       = clean_text(article.get("title", ""))
        description = clean_text(article.get("description", ""))
        url         = article.get("url", "")
        published   = article.get("publishedAt", "")

        # Skip articles with missing critical fields
        if not title or not url:
            continue

        # Skip removed articles (NewsAPI sometimes returns these)
        if title == "[Removed]":
            continue

        cleaned_articles.append({
            "title":       title,
            "description": description,
            "url":         url,
            "publishedAt": published,
        })

    return cleaned_articles