from src.vectordb.vector_store import get_vector_db

def query_data(query_text: str, similarity_threshold: float = 0.7, k: int = 3):    
    # Use the global vector db instance
    vector_db = get_vector_db()
    
    if vector_db is None:
        print("No vector database available. Please create one first.")
        return []
    
    # get relevant queries
    results = vector_db.similarity_search_with_relevance_scores(query=query_text, k=k)
    if len(results) == 0 or results[0][1] < similarity_threshold:
        print(f"Unable to find matching results.")
        return []
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    return results
