from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.output_parser import StrOutputParser
from langchain_community.embeddings import HuggingFaceEmbeddings

# from langchain.schema import HumanMessage, AIMessage
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# -------------------- Setup Logging --------------------
logging.basicConfig(
    filename="rag_chatbot.log",
    filemode="a",  # Append to file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- Load Environment Variables --------------------
load_dotenv()
# if not os.getenv("OPENAI_API_KEY"):
#     logger.critical("OPENAI_API_KEY not found in environment variables.")
#     raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")




# -------------------- Prompt Template --------------------

custom_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful resume screening assistant for recruiters.
Instructions:
1. Understand the user message.
2. Respond conversationally and naturally.
3. Use the context from job descriptions if available, otherwise say: "This job description is not available."
4. If the topic is totally unrelated (e.g., cooking, sports), politely say: "Sorry, I can only assist with resume screening and job descriptions."
5. For screening: If a resume PDF is attached/uploaded, use tools like search_pdf_attachment or browse_pdf_attachment to analyze it. Compare to JD context and give a match score (0-100%), strengths, weaknesses, and recommendations. If multiple resumes are provided, screen each one separately and rank them.

Here's the relevant context from Job Description documents:
{context}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])


# -------------------- Core Models and Memory --------------------
#embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    encode_kwargs={'normalize_embeddings': True}
)

#llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", temperature=0.2, streaming=True)
llm_model = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.2,streaming=True)
memory = ConversationBufferWindowMemory(k=6, return_messages=True)
summaryllm=ChatGroq(model="llama-3.1-8b-instant",temperature=0.6,streaming=True)



# -------------------- Vector Store --------------------
def load_vector_store():
    db_path = "chroma_db"
    logger.info("Attempting to load vector store...")
    try:
        if os.path.exists(db_path):
            vector_store = Chroma(persist_directory=db_path, embedding_function=embeddings)
            logger.info("Vector store loaded successfully.")
            return vector_store
        else:
            logger.warning("Vector store directory not found.")
            return None
    except Exception as e:
        logger.error(f"Failed to load vector store: {e}")
        return None



# -------------------- Retriever --------------------
def get_retriever(vector_store):
    logger.info("Creating retriever with MMR settings.")
    try:
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 2,
                "fetch_k": 5,
                "lambda_mult": 0.7
            }
        )
        return retriever
    except Exception as e:
        logger.error(f"Failed to create retriever: {e}")
        return None




# -------------------- Context Formatter --------------------
def get_context_with_metadata(documents):
    try:
        if not documents:
            logger.info("No documents retrieved for context.")
            return "No relevant BSK services found for this query."

        logger.info(f"Formatting context for {len(documents)} retrieved documents.")
        context_parts = []
        for i, doc in enumerate(documents, 1):
            service_info = f"Job Description {i}:\n{doc.page_content}"
            if hasattr(doc, 'metadata') and doc.metadata:
                metadata_str = " | ".join([f"{k}: {v}" for k, v in doc.metadata.items() if v])
                if metadata_str:
                    service_info += f"\n[Metadata: {metadata_str}]"
            context_parts.append(service_info)

        return "\n\n".join(context_parts)
    except Exception as e:
        logger.error(f"Error formatting context: {e}")
        return "Error processing retrieved documents."



# -------------------- Extract Job Query for Retrieval --------------------
def extract_job_query(input_str):
    if "\n\nScreen the following resumes:" in input_str:
        return input_str.split("\n\nScreen the following resumes:")[0]
    else:
        return input_str


# -------------------- RAG Chain Creation --------------------
def create_rag_chain():
    logger.info("Creating RAG chain...")
    try:
        vector_store = load_vector_store()
        if not vector_store:
            logger.error("Vector store unavailable. Chain not created.")
            return None

        retriever = get_retriever(vector_store)
        if not retriever:
            logger.error("Retriever creation failed. Chain not created.")
            return None

        chain = (
            {
                "context": lambda x: get_context_with_metadata(retriever.invoke(extract_job_query(x["input"]))),
                "history": lambda x: memory.load_memory_variables({})["history"],
                "input": lambda x: x["input"]
            }
            | custom_prompt_template
            | llm_model
            | StrOutputParser()
        )

        logger.info("RAG chain created successfully.")
        return chain
    except Exception as e:
        logger.error(f"Failed to create RAG chain: {e}")
        return None



# -------------------- Initialize Chain --------------------
rag_chain = create_rag_chain()



# -------------------- Answer Query --------------------
def answer_query(query):
    logger.info(f"Received query: {query}")
    if not rag_chain:
        error_msg = "Error: Could not load vector store."
        logger.error(error_msg)
        yield error_msg
        return

    try:
        full_response = ""
        for chunk in rag_chain.stream({"input": query}):
            full_response += chunk
            yield chunk

        memory.save_context({"input": query}, {"output": full_response})
        logger.info("Saved conversation context to memory.")

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logger.error(error_msg)
        yield error_msg

# -------------------- Clear Memory --------------------
def clear_memory():
    try:
        global memory
        memory.clear()
        logger.info("Memory cleared.")
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")

# -------------------- Load Chat History to Memory --------------------
def load_chat_to_memory(chat_messages):
    """Load chat messages into the conversation memory."""
    try:
        global memory
        # Clear existing memory first
        memory.clear()
        
        # Load messages into memory (skip the last few to stay within window limit)
        # We'll load in pairs (user message + assistant response)
        message_pairs = []
        for i in range(0, len(chat_messages) - 1, 2):
            if i + 1 < len(chat_messages):
                user_msg = chat_messages[i]
                assistant_msg = chat_messages[i + 1]
                
                if user_msg["role"] == "user" and assistant_msg["role"] == "Virtual Assistant":
                    message_pairs.append((user_msg["content"], assistant_msg["content"]))
        
        # Load the most recent message pairs (within memory window limit)
        # Since memory has k=6, we can load up to 3 conversation pairs
        recent_pairs = message_pairs[-3:] if len(message_pairs) > 3 else message_pairs
        
        for user_content, assistant_content in recent_pairs:
            memory.save_context({"input": user_content}, {"output": assistant_content})
        
        logger.info(f"Loaded {len(recent_pairs)} conversation pairs into memory.")
        
    except Exception as e:
        logger.error(f"Error loading chat to memory: {e}")

# -------------------- System Status --------------------
def get_system_status():
    logger.info("System status requested.")
    try:
        status = {
            "rag_chain_initialized": rag_chain is not None,
            "memory_conversations": len(memory.load_memory_variables({}).get("history", [])),
            "vector_store_available": load_vector_store() is not None,
            "timestamp": datetime.now().isoformat()
        }
        return status
    except Exception as e:
        logger.error(f"Error retrieving system status: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}
    

# #----------------------Summary LLM---------------------------
# def chat_title()