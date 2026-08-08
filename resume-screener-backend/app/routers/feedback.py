from fastapi import APIRouter
from pydantic import BaseModel

from ..feedback_store import log_feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackIn(BaseModel):
    session_id: int
    message_index: int
    question: str
    rating: int


@router.post("")
def submit_feedback(payload: FeedbackIn):
    log_feedback(payload.session_id, payload.message_index, payload.question, payload.rating)
    return {"ok": True}
