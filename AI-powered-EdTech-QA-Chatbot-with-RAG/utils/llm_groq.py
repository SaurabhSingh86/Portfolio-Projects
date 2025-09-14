# llm_groq.py

from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

def load_groq_llm(api_key: str, model_name: str = "llama-3.3-70b-versatile"):
    """
    Initialize Groq LLM (default: LLaMA 3 8B).
    """
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name=model_name,
        temperature=0.2  # lower temp = more factual, less creative
    )
    return llm


def build_qa_chain(vectorstore, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
    """
    Build a RetrievalQA chain using Groq + Vectorstore retriever.
    """
    llm = load_groq_llm(api_key, model_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # top 3 chunks
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",  # simplest approach
        return_source_documents=True
    )
    return qa_chain


def get_answer(qa_chain, query: str):
    """
    Run a query through the QA chain and return both answer + sources.
    """
    result = qa_chain(query)
    answer = result["result"]

    sources = []
    for doc in result.get("source_documents", []):
        sources.append(doc.page_content[:300])  # take preview of each source

    return answer, sources
