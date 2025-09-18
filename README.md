Resume Screening Bot
An AI-powered virtual assistant designed for recruiters and HR professionals to streamline resume screening against job descriptions. Built with Streamlit, LangChain, and advanced RAG (Retrieval-Augmented Generation) technology, this tool provides intelligent analysis, match scoring, and candidate evaluation.
🚀 Features

Intelligent Resume Screening: Upload multiple PDF resumes and screen them against job descriptions with automated match scoring (0-100%), strengths, weaknesses, and recommendations.
Job Description Integration: Leverages vector stores for contextual retrieval from job description documents.
Conversational Interface: Natural language chat for querying job details, evaluating candidates, and getting insights.
Chat History Management: Save, load, and manage multiple chat sessions with persistent history.
Feedback System: Rate responses to improve model performance over time.
Multi-Model Support: Compatible with Groq, OpenAI, and Google Generative AI models for flexible deployment.
Secure & Local: Runs locally with optional cloud integrations; no external dependencies for core functionality.

🛠️ Technology Stack

Frontend: Streamlit for an intuitive web-based UI.
Backend: LangChain for RAG pipelines, Chroma for vector database.
Embeddings: Hugging Face BGE models for semantic search.
LLM: Groq Llama models (with support for OpenAI and Gemini).
PDF Processing: PyPDF2 for resume parsing.
Memory & Logging: Conversation buffer memory with comprehensive logging.

📋 Prerequisites

Python 3.8+
GitHub account
API keys for LLM providers (Groq, OpenAI, or Google AI Studio)

💻 Installation

Clone the repository:
git clone https://github.com/yourusername/resume-screening-bot.git
cd resume-screening-bot


Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Set up environment variables:Create a .env file in the root directory and add your API keys:
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
GOOGLE_API_KEY=your_google_api_key  # Optional


Run the application:
streamlit run app.py



🔧 Usage

Start a New Chat: Click "New Chat" to begin a screening session.
Upload Resumes: Use the file uploader to add PDF resumes (appears by default in new chats).
Query the Bot: Ask questions like "Screen these resumes for the Software Engineer role" or "Evaluate candidate fit for JD".
Review Results: Get detailed analysis, scores, and rankings for multiple resumes.
Manage History: Switch between chats, delete sessions, and provide feedback on responses.
Toggle Uploads: Use the "Upload New Resumes" button to add more files mid-session.

For screening multiple resumes, ensure your query includes keywords like "screen", "evaluate", or "assess" to trigger analysis.
📁 Project Structure
resume-screening-bot/
├── app.py                 # Main Streamlit UI
├── RAG_chatbot.py         # RAG pipeline and LLM integration
├── requirements.txt       # Dependencies
├── .env.example           # Environment variables template
├── chroma_db/             # Vector store (auto-generated)
├── chat_history.json      # Persistent chat data
└── README.md              # This file

🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the project.
Create a feature branch (git checkout -b feature/AmazingFeature).
Commit your changes (git commit -m 'Add some AmazingFeature').
Push to the branch (git push origin feature/AmazingFeature).
Open a Pull Request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

LangChain for the RAG framework.
Streamlit for the rapid UI development.
Hugging Face and Groq for open-source models and APIs.
The open-source community for invaluable tools and libraries.

📞 Support
If you encounter issues or have suggestions, please open an issue on GitHub or reach out via email.

Built with ❤️ for efficient HR processes.
