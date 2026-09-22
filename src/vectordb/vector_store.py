import os
import shutil
from langchain_chroma import Chroma
from src.embeddings.embedder import get_embedder

CHROMA_PATH = 'chroma_db'

# Global variable for vector database
_vector_db = None

def get_vector_db():
    """
    Returns the global vector database instance.
    """
    global _vector_db
    if _vector_db is None:
        if os.path.exists(CHROMA_PATH):
            _vector_db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=get_embedder()
            )
            print(f"Loaded existing vector database from {CHROMA_PATH}")
        else:
            print("No existing vector database found.")
    return _vector_db

def save_chomadb(chunks, overwrite=False):
    """
    Save documents to Chroma DB
    Args:
        chunks: Document chunks to save
        overwrite: Whether to overwrite existing DB or extend it
    """
    global _vector_db
    
    if overwrite and os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        _vector_db = None  
    
    if _vector_db is None:
        # Create new DB
        _vector_db = Chroma.from_documents(
            chunks, 
            get_embedder(),
            persist_directory=CHROMA_PATH
        )
        print(f"Created new vector database with {len(chunks)} chunks.")
    else:
        # Add new documents to existing DB
        _vector_db.add_documents(chunks)
        print(f"Added {len(chunks)} chunks to existing vector database.")
    
    return _vector_db

def close_vector_db():
    """
    Close the vector database and release resources
    """
    global _vector_db
    if _vector_db is not None:
        _vector_db = None
        print("Vector database connection closed.")

def delete_chat_data(chat_id):
    """
    Delete all vector data associated with a specific chat_id
    """
    vector_db = get_vector_db()
    if vector_db is not None:
        try:
            # Langchain's Chroma wrapper provides access to the underlying collection
            vector_db._collection.delete(where={"chat_id": str(chat_id)})
            print(f"Successfully deleted vector data for chat_id: {chat_id}")
        except Exception as e:
            print(f"Error deleting vector data for chat_id {chat_id}: {e}")

