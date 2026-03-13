from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    ticker: str