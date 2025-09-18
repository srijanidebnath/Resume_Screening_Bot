Resume Screening Bot

A powerful AI-powered virtual assistant designed for recruiters and HR professionals to streamline resume screening and candidate evaluation. Leveraging Retrieval-Augmented Generation (RAG) technology, this tool intelligently analyzes resumes against job descriptions, providing match scores, strengths, weaknesses, and recommendations.

✨ Features

Automated Resume Screening: Upload multiple PDF resumes and screen them against job descriptions with match scores (0-100%), detailed strengths, weaknesses, and recommendations.
Contextual Job Description Analysis: Uses a vector store to retrieve relevant job description details for accurate responses.
Conversational Interface: Natural language chat for querying job details and candidate evaluations.
Chat History Management: Save, load, and delete chat sessions with persistent history stored in JSON.
Feedback System: Rate assistant responses to improve performance over time.
Multi-LLM Support: Compatible with Groq (Llama), OpenAI, and Google Generative AI models.
Local Deployment: Runs locally with optional cloud integrations for flexibility.


🛠️ Tech Stack

Frontend: Streamlit for a sleek, web-based UI.
Backend: LangChain for RAG pipelines, Chroma for vector storage.
Embeddings: Hugging Face BGE for semantic search.
LLM: Groq Llama models, with optional OpenAI and Google Gemini support.
PDF Processing: PyPDF2 for parsing resume PDFs.
Utilities: Conversation buffer memory, logging, and environment variable management.


📋 Prerequisites

Python: Version 3.8 or higher
GitHub Account: For repository management
API Keys: Required for LLM providers (Groq, OpenAI, or Google AI Studio)


🚀 Installation

Clone the Repository:
git clone https://github.com/yourusername/resume-screening-bot.git
cd resume-screening-bot


Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Set Up Environment Variables:Create a .env file in the project root and add your API keys:
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
GOOGLE_API_KEY=your_google_api_key  # Optional


Run the Application:
streamlit run app.py




🎯 Usage

Start a New Chat: Click the "New Chat" button to begin a new screening session.
Upload Resumes: Use the file uploader (shown by default in new chats) to add PDF resumes.
Query the Assistant: Ask questions like "Screen these resumes for a Software Engineer role" or "Evaluate candidate fit for this JD".
Review Results: Receive detailed analysis, including match scores and rankings for multiple resumes.
Toggle File Uploader: Use the "Upload New Resumes" button in the query bar to add more resumes mid-session.
Manage Chats: Switch between saved chats, delete sessions, or rate responses for feedback.

Note: For resume screening, include keywords like "screen", "evaluate", "assess", "review", or "match" in your query to trigger analysis of uploaded resumes.

📂 Project Structure
resume-screening-bot/
├── app.py                 # Streamlit UI for the application
├── RAG_chatbot.py         # RAG pipeline and LLM logic
├── requirements.txt       # Project dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Excludes sensitive files (e.g., .env, chroma_db)
├── chat_history.json      # Stores chat session data
├── feedback_YYYY-MM-DD.json  # Stores user feedback (generated)
├── chroma_db/             # Vector store directory (generated)
└── README.md              # Project documentation


🤝 Contributing
We welcome contributions to enhance the Resume Screening Bot! To contribute:

Fork the repository.
Create a feature branch:git checkout -b feature/YourFeature


Commit your changes:git commit -m "Add YourFeature"


Push to the branch:git push origin feature/YourFeature


Open a Pull Request on GitHub.

Please ensure your code follows the project's style and includes tests where applicable.

📜 License
This project is licensed under the MIT License.

🙌 Acknowledgments

LangChain for the RAG framework.
Streamlit for rapid UI development.
Groq and Hugging Face for powerful AI models.
The open-source community for providing robust tools and libraries.


📬 Contact & Support
For issues, feature requests, or questions, please:

Open an issue on the GitHub Issues page.
Contact the maintainer via email (replace with your email if desired).


Empowering recruiters with AI-driven efficiency. Built with ❤️ for HR excellence.
