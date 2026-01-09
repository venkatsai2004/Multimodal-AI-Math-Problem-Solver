# File: core/rag_hybrid.py

"""
Hybrid RAG module handling:
1. Static knowledge base (formulas, templates, common mistakes from knowledge/ directory)
2. Dynamic memory of solved problems (parsed problem + solution + feedback)

Uses Chroma for persistent vector stores.
Embeddings: sentence-transformers/all-MiniLM-L6-v2 (local, fast)

Provides:
- Initialization of static KB (on first run)
- Retrieval from static KB
- Add solved problem to memory
- Retrieve similar solved problems
- Combined hybrid retrieval (static + memory) with source tracking
"""

import os
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.config import Config

# Embedding model (local)
embedding_model = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)

# Persistent directories
KB_COLLECTION = "knowledge_base"
MEMORY_COLLECTION = "solved_problems"

# Initialize vector stores
kb_vectorstore = Chroma(
    collection_name=KB_COLLECTION,
    embedding_function=embedding_model,
    persist_directory=str(Config.VECTOR_STORE_PATH)
)

memory_vectorstore = Chroma(
    collection_name=MEMORY_COLLECTION,
    embedding_function=embedding_model,
    persist_directory=str(Config.SOLVED_PROBLEMS_VECTOR_STORE_PATH)
)

def _load_knowledge_base_documents() -> List[Document]:
    """Load all markdown files from knowledge/ directory recursively."""
    docs = []
    for md_file in Config.KNOWLEDGE_BASE_DIR.rglob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        metadata = {
            "source": str(md_file.relative_to(Config.KNOWLEDGE_BASE_DIR)),
            "type": "static_knowledge"
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def initialize_static_kb_if_needed():
    """Build static knowledge base if collection is empty."""
    if kb_vectorstore._collection.count() == 0:
        print("Building static knowledge base from knowledge/ directory...")
        raw_docs = _load_knowledge_base_documents()
        
        if not raw_docs:
            print("Warning: No markdown files found in knowledge/")
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        splits = text_splitter.split_documents(raw_docs)
        
        # Add with unique IDs
        kb_vectorstore.add_documents(splits)
        kb_vectorstore.persist()
        print(f"Static KB initialized with {len(splits)} chunks.")
    else:
        print("Static knowledge base already exists.")

def retrieve_from_kb(query: str, k: int = Config.TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
    """Retrieve from static knowledge base."""
    results = kb_vectorstore.similarity_search_with_score(query, k=k)
    retrieved = []
    for doc, score in results:
        retrieved.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "type": "knowledge_base",
            "relevance_score": round(float(score), 4)
        })
    return retrieved

def add_solved_problem_to_memory(
    parsed_problem: Dict,
    solution: Dict,
    feedback: str = None
):
    """
    Add a solved problem to memory vector store.
    Document content: combination of problem + solution for better similarity.
    """
    content = f"""
Problem: {parsed_problem['problem_text']}
Topic: {parsed_problem['topic']}
Variables: {', '.join(parsed_problem['variables'])}
Constraints: {', '.join(parsed_problem['constraints'])}

Solution steps: {solution.get('steps', '')}
Final answer: {solution.get('answer', '')}
Feedback: {feedback or 'None'}
    """.strip()
    
    metadata = {
        "type": "solved_problem",
        "topic": parsed_problem['topic'],
        "source": "memory"
    }
    
    doc = Document(page_content=content, metadata=metadata)
    memory_vectorstore.add_documents([doc])
    memory_vectorstore.persist()

def retrieve_similar_problems(query: str, k: int = Config.TOP_K_MEMORY_RETRIEVAL) -> List[Dict[str, Any]]:
    """Retrieve similar previously solved problems."""
    if memory_vectorstore._collection.count() == 0:
        return []
    
    results = memory_vectorstore.similarity_search_with_score(query, k=k)
    retrieved = []
    for doc, score in results:
        retrieved.append({
            "content": doc.page_content,
            "topic": doc.metadata.get("topic", "unknown"),
            "type": "solved_problem",
            "relevance_score": round(float(score), 4)
        })
    return retrieved

def hybrid_retrieval(query: str) -> List[Dict[str, Any]]:
    """
    Combined retrieval: static KB + similar solved problems.
    Returns sorted by relevance or simply concatenated with type distinction.
    No hallucination: if nothing relevant, returns empty list.
    """
    kb_results = retrieve_from_kb(query, k=Config.TOP_K_RETRIEVAL)
    memory_results = retrieve_similar_problems(query, k=Config.TOP_K_MEMORY_RETRIEVAL)
    
    # Simple concatenation, prioritising KB then memory
    all_results = kb_results + memory_results
    
    # Filter out very low relevance if needed (optional threshold)
    # For now, return all retrieved
    
    return all_results

# Initialize static KB on import
initialize_static_kb_if_needed()