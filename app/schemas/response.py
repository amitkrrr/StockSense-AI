from pydantic import BaseModel
from typing import Optional, List

class ArticleSchema(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    publishedAt: str

class AnalyzeResponse(BaseModel):
    ticker: str
    article_count: int
    articles: List[ArticleSchema]