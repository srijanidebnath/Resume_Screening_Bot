"""
Same chat_history.json approach your Streamlit app used — a plain JSON file
keyed by chat id. Kept as JSON (rather than a real database) on purpose, so
your existing chat_history.json file just drops in and works.
"""
import json
import os
from datetime import datetime

CHAT_HISTORY_FILE = "chat_history.json"

# Kept as "Virtual Assistant" internally to match your existing
# chat_history.json and RAG_chatbot.load_chat_to_memory(), which checks for
# this exact string. The API layer translates it to "assistant" for the frontend.
ASSISTANT_ROLE = "Virtual Assistant"


def load_chat_history() -> dict:
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_chat_history(chat_data: dict) -> None:
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)


def get_next_chat_id(chat_data: dict) -> int:
    if not chat_data:
        return 1
    return max(int(k) for k in chat_data.keys()) + 1


def create_chat() -> dict:
    chat_data = load_chat_history()
    new_id = get_next_chat_id(chat_data)
    entry = {
        "created_at": datetime.now().isoformat(),
        "title": f"Chat {new_id}",
        "messages": [],
    }
    chat_data[str(new_id)] = entry
    save_chat_history(chat_data)
    return {"id": new_id, **entry}


def delete_chat(chat_id: int) -> bool:
    chat_data = load_chat_history()
    key = str(chat_id)
    if key in chat_data:
        del chat_data[key]
        save_chat_history(chat_data)
        return True
    return False


def get_chat(chat_id: int):
    chat_data = load_chat_history()
    return chat_data.get(str(chat_id))


def update_chat_title(chat_id: int, first_message: str) -> None:
    chat_data = load_chat_history()
    key = str(chat_id)
    if key in chat_data:
        chat_data[key]["title"] = first_message[:10] + "..."
        save_chat_history(chat_data)


def save_message(chat_id: int, role: str, content: str) -> None:
    chat_data = load_chat_history()
    key = str(chat_id)
    if key in chat_data:
        chat_data[key]["messages"].append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        save_chat_history(chat_data)
