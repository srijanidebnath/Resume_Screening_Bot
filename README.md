# 📌 Resume Screening Bot

A powerful AI-powered virtual assistant designed for recruiters and HR professionals to streamline resume screening and candidate evaluation.
Leveraging Retrieval-Augmented Generation (RAG), this tool intelligently analyzes resumes against job descriptions, providing match scores, strengths, weaknesses, and recommendations.

**✨ Features**

* Automated Resume Screening: Upload multiple PDF resumes and screen them against job descriptions with match scores (0-100%), detailed strengths, weaknesses, and recommendations.
* Contextual Job Description Analysis: Uses a Chroma vector store to retrieve relevant job description details for accurate responses.
* Conversational Interface: Natural language chat for querying job details and candidate evaluations, with streamed responses.
* Chat History Management: Create, switch between, and delete chat sessions with persistent history stored in JSON.
* Feedback System: Rate assistant responses to help track performance over time.
* Job Description Vector DB Page: Add, update, or delete indexed job description PDFs directly from the browser.
* Multi-LLM Ready: Built around Groq (Llama) by default, with LangChain making it straightforward to swap in OpenAI or Google Generative AI models.

**🛠️ Tech Stack**

* Frontend: React (Vite) — JavaScript, HTML, CSS
* Backend: FastAPI (Python)
* RAG Pipeline: LangChain
* Vector Store: ChromaDB
* Embeddings: Hugging Face BGE (`BAAI/bge-small-en-v1.5`) for semantic search
* LLM: Groq Llama models
* PDF Processing: PyPDF for parsing resumes and job descriptions
* Utilities: Conversation buffer memory, logging, and environment variable management

**📋 Prerequisites**

* Python: Version 3.11 recommended
* Node.js: Version 18 or higher
* GitHub Account: For repository management
* API Keys: Required for the LLM provider
* GROQ_API_KEY

**🚀 Installation**

```
# Clone the Repository
git clone https://github.com/srijanidebnath/Resume_Screening_Bot.git
cd Resume_Screening_Bot
```

**Backend setup**

```
cd resume-screener-backend

# Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

Set Up Environment Variables
Create a `.env` file inside `resume-screener-backend/` and add your API key:

```
GROQ_API_KEY=your_groq_api_key
```

Run the backend:

```
uvicorn app.main:app --reload --port 8000
```

**Frontend setup**

```
cd resume-screener-frontend

# Install Dependencies
npm install

# Run the app
npm run dev
```

Open **http://localhost:5173** in your browser. The sidebar should show **● connected** once the backend is reachable.

**🎯 Usage**

1. Index a Job Description – Go to the Vector DB page and upload a job description PDF; it's chunked, embedded, and stored for retrieval.
2. Start a New Chat – Click New Chat to begin a screening session.
3. Attach Resumes – Use the file uploader in the chat composer to add candidate resume PDFs.
4. Query the Assistant – Example queries:
   * "Screen these resumes for a Software Engineer role"
   * "Evaluate candidate fit for this JD"
5. Review Results – Get a detailed analysis, including match scores, strengths, weaknesses, and recommendations.
6. Manage Chats – Switch between, or delete, past chat sessions from the sidebar.
7. Give Feedback – Rate assistant responses using the rating stars.

💡 Tip: Use keywords like screen, evaluate, assess, review, or match in your message to trigger resume screening — otherwise attached resumes are ignored.

**📂 Project Structure**

```
Resume_Screening_Bot/
├── resume-screener-frontend/       # React + Vite app
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── api.js                  # backend API client
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       ├── pages/
│       │   ├── ChatPage.jsx
│       │   └── VectorDbPage.jsx
│       └── components/
│           ├── Sidebar.jsx
│           ├── Navbar.jsx
│           ├── MessageBubble.jsx
│           └── RatingStars.jsx
│
└── resume-screener-backend/        # FastAPI app
    ├── requirements.txt
    ├── .env.example
    └── app/
        ├── main.py                 # FastAPI app, CORS, router wiring
        ├── rag_chatbot.py          # RAG pipeline (retrieval + LLM chain)
        ├── vector_store.py         # Chroma vector DB operations
        ├── chat_store.py           # chat_history.json read/write helpers
        ├── feedback_store.py       # feedback JSON helpers
        └── routers/
            ├── chats.py            # /api/chats/*  (incl. streaming /query)
            ├── vector_db.py        # /api/vector-db/*
            └── feedback.py         # /api/feedback
```

**🤝 Contributing**

We welcome contributions to enhance the Resume Screening Bot!

1. Fork the repository
2. Create a feature branch:

```
git checkout -b feature/YourFeature
```

3. Commit your changes:

```
git commit -m "Add YourFeature"
```

4. Push to the branch:

```
git push origin feature/YourFeature
```

5. Open a Pull Request

✅ Ensure your code follows the project's style and includes tests where applicable.

**📜 License**

This project is licensed under the MIT License.
