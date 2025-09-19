
# 📌 Resume Screening Bot

A powerful **AI-powered virtual assistant** designed for recruiters and HR professionals to streamline **resume screening** and **candidate evaluation**.  
Leveraging **Retrieval-Augmented Generation (RAG)**, this tool intelligently analyzes resumes against job descriptions, providing **match scores, strengths, weaknesses, and recommendations**.

---

## ✨ Features

- **Automated Resume Screening**: Upload multiple PDF resumes and screen them against job descriptions with match scores (0-100%), detailed strengths, weaknesses, and recommendations.  
- **Contextual Job Description Analysis**: Uses a vector store to retrieve relevant job description details for accurate responses.  
- **Conversational Interface**: Natural language chat for querying job details and candidate evaluations.  
- **Chat History Management**: Save, load, and delete chat sessions with persistent history stored in JSON.  
- **Feedback System**: Rate assistant responses to improve performance over time.  
- **Multi-LLM Support**: Compatible with **Groq (Llama)**, **OpenAI**, and **Google Generative AI** models.  
- **Local Deployment**: Runs locally with optional cloud integrations for flexibility.  

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit for a sleek, web-based UI.  
- **Backend**: LangChain for RAG pipelines, Chroma for vector storage.  
- **Embeddings**: Hugging Face BGE for semantic search.  
- **LLM**: Groq Llama models, with optional OpenAI and Google Gemini support.  
- **PDF Processing**: PyPDF2 for parsing resume PDFs.  
- **Utilities**: Conversation buffer memory, logging, and environment variable management.  

---

## 📋 Prerequisites

- **Python**: Version 3.8 or higher  
- **GitHub Account**: For repository management  
- **API Keys**: Required for LLM providers  
  - **GROQ_API_KEY**  
  - **OPENAI_API_KEY** *(optional)*  
  - **GOOGLE_API_KEY** *(optional)*  

---

## 🚀 Installation

```bash
# Clone the Repository
git clone https://github.com/yourusername/resume-screening-bot.git
cd resume-screening-bot

# Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
````

### Set Up Environment Variables

Create a `.env` file in the project root and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
GOOGLE_API_KEY=your_google_api_key  # Optional
```

### Run the Application

```bash
streamlit run app.py
```

---

## 🎯 Usage

1. **Start a New Chat** – Click the **New Chat** button to begin a new screening session.
2. **Upload Resumes** – Use the file uploader to add PDF resumes.
3. **Query the Assistant** – Example queries:

   * **"Screen these resumes for a Software Engineer role"**
   * **"Evaluate candidate fit for this JD"**
4. **Review Results** – Get detailed analysis, including **match scores** and **rankings**.
5. **Toggle File Uploader** – Add more resumes mid-session.
6. **Manage Chats** – Switch, delete, or rate chat sessions for feedback.

💡 **Tip**: Use keywords like **screen**, **evaluate**, **assess**, **review**, or **match** in your query to trigger resume screening.

---

## 📂 Project Structure

```
resume-screening-bot/
├── app.py                   # Streamlit UI
├── RAG_chatbot.py           # RAG pipeline and LLM logic
├── requirements.txt         # Dependencies
├── .env.example             # Template for environment variables
├── .gitignore               # Excludes sensitive files
├── chat_history.json        # Stores chat session data
├── feedback_YYYY-MM-DD.json # Stores user feedback
├── chroma_db/               # Vector store directory
└── README.md                # Project documentation
```

---

## 🤝 Contributing

We welcome contributions to enhance the **Resume Screening Bot**!

1. **Fork** the repository
2. Create a feature branch:

   ```bash
   git checkout -b feature/YourFeature
   ```
3. **Commit** your changes:

   ```bash
   git commit -m "Add YourFeature"
   ```
4. **Push** to the branch:

   ```bash
   git push origin feature/YourFeature
   ```
5. Open a **Pull Request**

✅ Ensure your code follows the project’s style and includes tests where applicable.

---

## 📜 License

This project is licensed under the **MIT License**.

---

