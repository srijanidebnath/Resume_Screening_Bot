import streamlit as st
import os
import tempfile
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain_community.document_loaders import PDFPlumberLoader
from vector_db_operations import delete_index_by_id, update_index, list_all_index_ids, persist_directory, embedding_function

# Title and description
st.title("Vector Database Management")
st.markdown("**Manage your vector database efficiently.** Add new job descriptions, delete or update existing ones, and view all stored job descriptions with ease.")

# Sidebar navigation
operation = st.sidebar.selectbox(
    "Select Operation",
    ["Add Job Descriptions", "Delete Job Descriptions", "Update Job Descriptions", "List Job Descriptions"],
    help="Choose an operation to perform on the vector database."
)

from vector_db_operations import list_all_index_ids

def get_scheme_names():
    ids = list_all_index_ids()
    return [id.replace('.pdf', '') for id in ids if id.endswith('.pdf')]

# Add Job Descriptions Section
if operation == "Add Job Descriptions":
    st.header("Add Job Descriptions")
    st.markdown("Upload PDF files to add new job descriptions to the vector database.")
    uploaded_files = st.file_uploader(
        "Upload PDF Job Descriptions", 
        type="pdf", 
        accept_multiple_files=True, 
        help="Select one or more PDF files to upload."
    )
    if st.button("Add to Vector DB", key="add_button"):
        if uploaded_files:
            existing_ids = set(list_all_index_ids())
            new_docs = []
            new_ids = []
            skipped = []
            with tempfile.TemporaryDirectory() as temp_dir:
                for uploaded_file in uploaded_files:
                    file_name = uploaded_file.name
                    if file_name in existing_ids:
                        skipped.append(file_name)
                        continue
                    file_path = os.path.join(temp_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    loader = PDFPlumberLoader(file_path)
                    docs = loader.load()
                    full_text = "\n".join([doc.page_content for doc in docs])
                    merged_doc = Document(page_content=full_text, metadata={"source": file_name})
                    new_docs.append(merged_doc)
                    new_ids.append(file_name)
            if new_docs:
                vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
                vectorstore.add_documents(new_docs, ids=new_ids)
                st.success(f"Successfully added {len(new_docs)} new job descriptions: {', '.join([id.replace('.pdf', '') for id in new_ids])}")
            if skipped:
                st.warning(f"Skipped {len(skipped)} existing job descriptions: {', '.join([s.replace('.pdf', '') for s in skipped])}")
        else:
            st.warning("Please upload at least one PDF file.")

# Delete Job Descriptions Section
elif operation == "Delete Job Descriptions":
    st.header("Delete Job Descriptions")
    st.markdown("Select a job description to remove from the vector database.")
    scheme_names = get_scheme_names()
    if scheme_names:
        selected_name = st.selectbox(
            "Select Job Description to Delete", 
            scheme_names, 
            help="Choose a job description to delete."
        )
        selected_id = selected_name + '.pdf'
        if st.button("Delete", key="delete_button"):
            delete_index_by_id(selected_id)
            st.success(f"Successfully deleted job description: {selected_name}")
    else:
        st.info("No job descriptions found in the vector database.")

# Update Job Descriptions Section
elif operation == "Update Job Descriptions":
    st.header("Update Job Descriptions")
    st.markdown("Select a job description and upload a new PDF to update it.")
    scheme_names = get_scheme_names()
    if scheme_names:
        selected_name = st.selectbox(
            "Select Job Description to Update", 
            scheme_names, 
            help="Choose a job description to update."
        )
        selected_id = selected_name + '.pdf'
        uploaded_file = st.file_uploader(
            "Upload New PDF", 
            type="pdf", 
            help="Upload the new PDF file to replace the existing job description."
        )
        if st.button("Update", key="update_button"):
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = temp_file.name
                update_index(selected_id, temp_path)
                os.remove(temp_path)
                st.success(f"Job Description '{selected_name}' updated successfully.")
            else:
                st.warning("Please upload a new PDF file.")
    else:
        st.info("No job descriptions found in the vector database.")

# List Job Descriptions Section
elif operation == "List Job Descriptions":
    st.header("List Job Descriptions")
    st.markdown("View all job descriptions currently stored in the vector database.")
    scheme_names = get_scheme_names()
    if scheme_names:
        st.write("**Stored Job Descriptions:**")
        for idx, name in enumerate(scheme_names, 1):
            st.write(f"{idx}. {name}")
    else:
        st.info("No job descriptions found in the vector database.")

# Footer
st.markdown("---")
st.markdown("*Developed for efficient vector database management in a business environment.*")