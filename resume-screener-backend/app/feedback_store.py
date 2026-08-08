"""Same feedback_YYYY-MM-DD.json logging your Streamlit app used."""
import json
import os
from datetime import datetime


def log_feedback(session_id: int, message_index: int, question: str, rating: int) -> None:
    feedback_file = f"feedback_{datetime.now().strftime('%Y-%m-%d')}.json"
    entry = {
        "session_id": session_id,
        "message_index": message_index,
        "question": question,
        "rating": rating,
        "timestamp": datetime.now().isoformat(),
    }

    data = []
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    for existing in data:
        if existing["session_id"] == session_id and existing["message_index"] == message_index:
            existing.update(entry)
            break
    else:
        data.append(entry)

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
