from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

def build_vector_store(chunks):
    """
    Convert text chunks into embeddings and store in FAISS.
    Returns the FAISS vector store.
    """
    # Use HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create FAISS index from chunks
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    return vector_store
