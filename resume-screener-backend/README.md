# Resume Screener — FastAPI backend

Wraps your existing `RAG_chatbot.py` and vector-store logic behind the REST
API your React frontend already expects.

## 1. Install dependencies

You said you've already got a venv with fastapi + uvicorn installed — activate
it, then install the rest:

```bash
pip install -r requirements.txt
```

## 2. Set your API key

```bash
cp .env.example .env
```

Open `.env` and paste in your Groq key (`RAG_chatbot.py` uses `ChatGroq`, so
this is the one that's actually required — OpenAI/Google keys stay optional
unless you switch models).

## 3. (Optional) bring over your old data

Drop your existing `chat_history.json`, any `feedback_*.json` files, and your
`chroma_db/` folder into this directory (next to `requirements.txt`) if you
want to keep the sessions and indexed job descriptions you already had from
the Streamlit version. Everything here reads/writes those same file formats.

## 4. Run it

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** — that's FastAPI's auto-generated Swagger
UI. You can try every endpoint from the browser before your React app even
touches it, which is the easiest way to sanity-check things as you're
learning FastAPI.

## 5. Connect the frontend

Nothing to change — the React app's Vite dev server already proxies `/api/*`
to `http://localhost:8000`. Just run both at once:

```bash
# terminal 1
cd resume-screener-backend && uvicorn app.main:app --reload --port 8000

# terminal 2
cd resume-screener-frontend && npm run dev
```

Once the backend is up, the "○ local preview" indicator in the navbar should
flip to "● connected".

## Project layout

```
resume-screener-backend/
├── requirements.txt
├── .env.example
└── app/
    ├── main.py            # FastAPI app, CORS, router wiring
    ├── rag_chatbot.py     # your existing RAG logic, unchanged
    ├── vector_store.py    # your vector_db_operations.py, refactored to be import-safe
    ├── chat_store.py      # chat_history.json read/write helpers
    ├── feedback_store.py  # feedback_YYYY-MM-DD.json helpers
    └── routers/
        ├── chats.py       # /api/chats/*  (incl. streaming /query)
        ├── vector_db.py   # /api/vector-db/*
        └── feedback.py    # /api/feedback
```
