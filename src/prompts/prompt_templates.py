PROMPT_TEMPLATE = """
You are a helpful AI assistant. 
First, try to answer the question using the provided context from the user's documents. 
If the context is empty or does not contain the answer, use your own internal knowledge or available tools to answer the question.

Context:
{context}

---------------
Question: {question}
"""
