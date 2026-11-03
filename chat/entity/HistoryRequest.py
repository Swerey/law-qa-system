from pydantic import BaseModel

class HistoryRequest(BaseModel):
    question: str
    answer: str
    parentId: str
    userId: str
