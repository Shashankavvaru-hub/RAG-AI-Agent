from src.vectordb.vector_store import get_vector_db

def query_data(query_text: str, similarity_threshold: float = 0.5, k: int = 3, chat_id=None):    
    # Use the global vector db instance
    vector_db = get_vector_db()
    
    if vector_db is None:
        print("No vector database available. Please create one first.")
        return []
    
    # get relevant queries
    filter_kwargs = {"chat_id": str(chat_id)} if chat_id else None
    results = vector_db.similarity_search_with_relevance_scores(
        query=query_text, 
        k=k,
        filter=filter_kwargs
    )
    
    if len(results) == 0 or results[0][1] < similarity_threshold:
        print(f"Unable to find matching results.")
        return []
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    return results
