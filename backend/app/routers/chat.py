from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ChatRequest, ChatResponse
from app.services.llm.assistant import answer_query

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    answer, context = answer_query(db, request.query)
    return ChatResponse(answer=answer, used_context=context)
