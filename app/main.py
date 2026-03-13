from fastapi import FastAPI, HTTPException
from app.schemas.request import AnalyzeRequest
from app.schemas.response import AnalyzeResponse, ArticleSchema
from app.services.news_fetcher import fetch_news_for_ticker

app = FastAPI(
    title="StockSense AI",
    description="AI-powered stock market sentiment analyzer",
    version="1.0.0"
)

@app.get("/")
async def health():
    return {"status": "ok", "service": "StockSense AI"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    # Step 1 — Clean and uppercase the ticker
    ticker = request.ticker.upper().strip()

    # Step 2 — Validate length
    if len(ticker) < 1 or len(ticker) > 10:
        raise HTTPException(
            status_code=400,
            detail="Ticker must be between 1 and 10 characters"
        )

    # Step 3 — Validate only letters allowed
    if not ticker.isalpha():
        raise HTTPException(
            status_code=400,
            detail="Ticker must contain letters only. Example: AAPL, TCS, INFY"
        )

    # Step 4 — Fetch news from NewsAPI
    try:
        raw_articles = await fetch_news_for_ticker(ticker)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch news: {str(e)}"
        )

    # Step 5 — Check if any articles came back
    if not raw_articles:
        raise HTTPException(
            status_code=404,
            detail=f"No news found for '{ticker}'. Check if it is a valid stock symbol."
        )

    # Step 6 — Map raw articles to ArticleSchema
    articles = []
    for a in raw_articles:
        if a.get("title") and a.get("url"):
            articles.append(ArticleSchema(
                title=a["title"],
                description=a.get("description"),
                url=a["url"],
                publishedAt=a["publishedAt"]
            ))

    # Step 7 — Return final response
    return AnalyzeResponse(
        ticker=ticker,
        article_count=len(articles),
        articles=articles
    )