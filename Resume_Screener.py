import streamlit as st
from RAG_chatbot import answer_query, clear_memory, get_system_status, load_chat_to_memory, load_vector_store, get_retriever
import time
import json
import os
from datetime import datetime
import tempfile
from langchain_community.document_loaders import PyPDFLoader

# Configure page settings (only once, here at the top)
st.set_page_config(
    page_title="Resume Screening Bot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# JSON file to store chat history
CHAT_HISTORY_FILE = "chat_history.json"


def load_chat_history():
    """Load chat history from JSON file."""
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        return {}

def save_chat_history(chat_data):
    """Save chat history to JSON file."""
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error("Error saving chat history")

def get_next_chat_id(chat_data):
    """Get the next available chat ID."""
    if not chat_data:
        return 1
    return max([int(k) for k in chat_data.keys()]) + 1

def create_new_chat():
    """Create a new chat session."""
    chat_data = load_chat_history()
    new_chat_id = get_next_chat_id(chat_data)
    
    # Create new chat entry
    chat_data[str(new_chat_id)] = {
        "created_at": datetime.now().isoformat(),
        "title": f"Chat {new_chat_id}",
        "messages": []
    }
    
    save_chat_history(chat_data)
    return new_chat_id

def update_chat_title(chat_id, first_message):
    """Update chat title based on first user message."""
    chat_data = load_chat_history()
    if str(chat_id) in chat_data:
        # Use first 30 characters of the first message as title
        title = first_message[:10] + "..." 
        chat_data[str(chat_id)]["title"] = title
        save_chat_history(chat_data)

def save_message_to_chat(chat_id, role, content):
    """Save a message to the specified chat."""
    chat_data = load_chat_history()
    if str(chat_id) in chat_data:
        chat_data[str(chat_id)]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        save_chat_history(chat_data)

def delete_chat(chat_id):
    """Delete a specific chat from history."""
    try:
        chat_data = load_chat_history()
        if str(chat_id) in chat_data:
            del chat_data[str(chat_id)]
            save_chat_history(chat_data)
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting chat: {str(e)}")
        return False

# Feedback logging function
def log_feedback(session_id, message_index, question, rating):
    current_date = datetime.now().strftime("%Y-%m-%d")
    feedback_file = f"feedback_{current_date}.json"
    feedback_entry = {
        "session_id": session_id,
        "message_index": message_index,
        "question": question,
        "rating": rating,
        "timestamp": datetime.now().isoformat()
    }
    try:
        if os.path.exists(feedback_file):
            with open(feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        # Find and update existing entry or append new one
        for entry in data:
            if entry["session_id"] == session_id and entry["message_index"] == message_index:
                entry.update(feedback_entry)
                break
        else:
            data.append(feedback_entry)
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Failed to log feedback: {e}")

# Custom CSS for better styling
st.markdown("""
<style>
.sidebar-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 1rem;
    font-weight: bold;
}
.chat-button {
    margin: 0.2rem 0;
}
.info-box {
    background: #1f77b4;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}
.stSelectbox > label {
    font-weight: bold;
    color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = create_new_chat()
    st.session_state.current_chat_messages = []
    st.session_state.is_new_chat = True
    st.session_state.show_delete_confirmation = None
    st.session_state.show_file_uploader = True  # Show uploader by default for new chat
    st.session_state.resume_docs = []  # Store resume documents

chat_data = load_chat_history()

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        📄 Resume Screener
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💬 Chat History")

    if st.button("✨ New Chat", use_container_width=True, type="primary"):
        clear_memory()
        st.session_state.current_chat_id = create_new_chat()
        st.session_state.current_chat_messages = []
        st.session_state.is_new_chat = True
        st.session_state.show_delete_confirmation = None
        st.session_state.show_file_uploader = True  # Reset to show uploader for new chat
        st.session_state.resume_docs = []  # Clear resume docs for new chat
        st.rerun()

    st.markdown("---")

    if chat_data:
        sorted_chats = sorted(chat_data.items(), key=lambda x: int(x[0]), reverse=True)
        for chat_id, chat_info in sorted_chats:
            chat_title = chat_info.get("title", f"Chat {chat_id}")
            col1, col2 = st.columns([4, 1])
            with col1:
                if int(chat_id) == st.session_state.current_chat_id:
                    st.button(f"🔸 {chat_title}", use_container_width=True)
                else:
                    if st.button(f"💬 {chat_title}", key=f"chat_{chat_id}", use_container_width=True):
                        st.session_state.current_chat_id = int(chat_id)
                        st.session_state.current_chat_messages = chat_info.get("messages", [])
                        st.session_state.is_new_chat = False
                        st.session_state.show_delete_confirmation = None
                        st.session_state.show_file_uploader = False  # Hide uploader when switching chats
                        if st.session_state.current_chat_messages:
                            load_chat_to_memory(st.session_state.current_chat_messages)
                        else:
                            clear_memory()
                        st.rerun()
            with col2:
                if int(chat_id) != st.session_state.current_chat_id:
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                        st.session_state.show_delete_confirmation = int(chat_id)
                        st.rerun()

    if st.session_state.show_delete_confirmation:
        st.markdown("---")
        st.markdown(f"""
        <div style="background: #1f77b4; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #1f77b4; margin: 1rem 0;">
            <strong>⚠️ Confirm Deletion</strong><br>
            Are you sure you want to delete Chat {st.session_state.show_delete_confirmation}?
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", key="confirm_delete", type="secondary"):
                if delete_chat(st.session_state.show_delete_confirmation):
                    st.success("Chat deleted successfully!")
                    st.session_state.show_delete_confirmation = None
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Failed to delete chat")
        with col2:
            if st.button("❌ Cancel", key="cancel_delete"):
                st.session_state.show_delete_confirmation = None
                st.rerun()

    st.markdown("---")

    st.subheader("📈 Session Info")
    current_time = datetime.now().strftime('%H:%M:%S')
    st.markdown(f"""
    <div class="info-box">
        <strong>Current Chat Session:</strong> #{st.session_state.current_chat_id}<br>
        <strong>Total Chats:</strong> {len(chat_data)}<br>
        <strong>Time:</strong> {current_time}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("📋 About This Project", expanded=False):
        st.markdown("""
        **Resume Screener** is an AI-powered virtual assistant designed specifically for 
        recruiters and HR professionals. It provides intelligent 
        support for job descriptions, resume screening, and candidate evaluation. 

        The system uses advanced RAG (Retrieval-Augmented Generation) technology 
        to deliver accurate, contextual responses based on job description documents.
        """)

chat_container = st.container()
with chat_container:
    if st.session_state.current_chat_messages:
        for i, message in enumerate(st.session_state.current_chat_messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="📄"):
                    st.write(message["content"])

                    # Always display the "Rate this answer?" button immediately
                    if st.button("Rate this answer?", key=f"rate_button_{i}"):
                        st.session_state[f"show_rating_{i}"] = True

                    # Display rating options only if button is clicked
                    if f"show_rating_{i}" in st.session_state and st.session_state[f"show_rating_{i}"]:
                        rating_options = ["★", "★★", "★★★", "★★★★", "★★★★★"]
                        selected_stars = st.radio(
                            "Rate this answer:",
                            rating_options,
                            key=f"rating_radio_{i}",
                            horizontal=True,
                            index=None
                        )
                        if selected_stars:
                            rating = len(selected_stars)
                            session_id = st.session_state.current_chat_id
                            question = st.session_state.current_chat_messages[i-1]["content"]
                            log_feedback(session_id, i, question, rating)
                            st.write("Thanks for your feedback")

    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>📝 No messages in this chat yet</h3>
            <p>Start a conversation to see messages here</p>
        </div>
        """, unsafe_allow_html=True)

if st.session_state.is_new_chat or int(st.session_state.current_chat_id) == st.session_state.current_chat_id:
    # Button to toggle file uploader visibility
    if st.button("📎 Upload New Resumes", key="toggle_uploader"):
        st.session_state.show_file_uploader = not st.session_state.show_file_uploader

    # Show file uploader if enabled (by default for new chat or when toggled)
    resume_temp_files = []
    if st.session_state.show_file_uploader:
        uploaded_resumes = st.file_uploader("Upload Resume PDF(s) to Screen", type="pdf", accept_multiple_files=True)
        if uploaded_resumes:
            st.session_state.resume_docs = []  # Clear previous resumes when new ones are uploaded
            for uploaded_resume in uploaded_resumes:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded_resume.getbuffer())
                    resume_path = temp_file.name
                    resume_temp_files.append(resume_path)
                loader = PyPDFLoader(resume_path)
                docs = loader.load()
                text = "\n\n".join([doc.page_content for doc in docs])
                st.session_state.resume_docs.append({"name": uploaded_resume.name, "text": text})
            st.success(f"{len(uploaded_resumes)} resume(s) uploaded successfully!")
            st.session_state.show_file_uploader = False  # Hide uploader after successful upload

    user_query = st.chat_input("💬 Ask about job descriptions or screen a resume...")
    if user_query:
        backend_query = user_query
        # Only append resume information if the query explicitly requests screening and resumes exist
        if st.session_state.resume_docs and any(keyword in user_query.lower() for keyword in ["screen", "evaluate", "assess", "review", "match"]):
            resumes_info = "\n\n".join([f"Resume {i+1}: {doc['name']}\n{doc['text']}" for i, doc in enumerate(st.session_state.resume_docs)])
            backend_query += f"\n\nScreen the following resumes:\n{resumes_info}"
        try:
            with st.chat_message("user", avatar="👤"):
                st.write(user_query)
            save_message_to_chat(st.session_state.current_chat_id, "user", user_query)
            st.session_state.current_chat_messages.append({
                "role": "user", 
                "content": user_query,
                "timestamp": datetime.now().isoformat()
            })
            if st.session_state.is_new_chat:
                update_chat_title(st.session_state.current_chat_id, user_query)
                st.session_state.is_new_chat = False

            with st.chat_message("assistant", avatar="📄"):
                response_placeholder = st.empty()
                full_response = ""
                with st.spinner("Resume Screener is thinking..."):
                    for chunk in answer_query(query=backend_query):
                        full_response += chunk
                        response_placeholder.markdown(full_response)
                        time.sleep(0.005)
                # After the response is complete, update the placeholder with both the response and the button
                message_index = len(st.session_state.current_chat_messages)  # Unique index for this message
                response_placeholder.markdown(f"{full_response}")  # Finalize the response
                if st.button("Rate this answer?", key=f"rate_button_{message_index}"):
                    st.session_state[f"show_rating_{message_index}"] = True
                # Show rating options if the button was clicked
                if f"show_rating_{message_index}" in st.session_state and st.session_state[f"show_rating_{message_index}"]:
                    rating_options = ["★", "★★", "★★★", "★★★★", "★★★★★"]
                    selected_stars = st.radio(
                        "Rate this answer:",
                        rating_options,
                        key=f"rating_radio_{message_index}",
                        horizontal=True,
                        index=None
                    )
                    if selected_stars:
                        rating = len(selected_stars)
                        session_id = st.session_state.current_chat_id
                        question = user_query
                        log_feedback(session_id, message_index, question, rating)
                        st.write("Thanks for your feedback")

            # Append the assistant's message to the chat history after rendering
            save_message_to_chat(st.session_state.current_chat_id, "Virtual Assistant", full_response)
            st.session_state.current_chat_messages.append({
                "role": "Virtual Assistant", 
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            })
            # No need for st.rerun() here, as the button is rendered immediately above
        except Exception as e:
            st.error("⚠️ An error occurred while processing your query. Please try again.")
            st.exception(e)
        finally:
            for path in resume_temp_files:
                if os.path.exists(path):
                    os.remove(path)
else:
    st.markdown("""
    <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px; 
                text-align: center; margin: 2rem 0; border-left: 4px solid #2196f3;">
        <h4>📖 Viewing Previous Chat</h4>
        <p>This is a previous conversation. Click '<strong>✨ New Chat</strong>' to start a new conversation.</p>
    </div>
    """, unsafe_allow_html=True)