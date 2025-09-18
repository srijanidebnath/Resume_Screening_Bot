import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

persist_directory = "./chroma_db"
embedding_function = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")


def create_vector_db():
    vectorstore = Chroma(
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
    print("Vector store created and persisted at", persist_directory)
    return vectorstore

# Initialize if not already present
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)
    create_vector_db()

def add_pdfs_to_db(folder_path:str):
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            file_path = os.path.join(folder_path, file)
            loader = PDFPlumberLoader(file_path)
            docs = loader.load()

            # Merge all pages into a single document
            full_text = "\n".join([doc.page_content for doc in docs])
            merged_doc = Document(page_content=full_text, metadata={"source": file})

            # Add with a unique ID (file name)
            vectorstore.add_documents([merged_doc], ids=[file])
            print(f"Added merged document for {file} to vector store.")

    print("All documents added successfully.")

add_pdfs_to_db("pdfs")

def delete_index_by_id(doc_id:str):
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
    vectorstore.delete(ids=[doc_id])
    print(f"Deleted index with ID: {doc_id}")


def update_index(doc_id, new_pdf_path):
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    # Delete old entry
    vectorstore.delete(ids=[doc_id])
    print(f"Deleted old entry with ID: {doc_id}")

    # Load new document and add
    loader = PDFPlumberLoader(new_pdf_path)
    docs = loader.load()
    vectorstore.add_documents(docs, ids=[doc_id]*len(docs))
    print(f"Updated index with ID: {doc_id}")

def list_all_index_ids():
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
    collection = vectorstore._collection
    results = collection.get()
    return results["ids"]

