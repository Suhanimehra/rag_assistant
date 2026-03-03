from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def chunk_text(text): #text in chunks 
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    
    return splitter.split_text(text)

def create_vector_store(chunks): #vector store create karne ke liye
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.from_texts(chunks, embeddings)

def save_vector_store(vector_store, path):
    os.makedirs(path, exist_ok=True)
    vector_store.save_local(path)

def load_vector_store(path):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )