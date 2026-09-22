from src.ingestion.loader import load_documents
from src.chunking.chunker import text_spliter
from src.vectordb.vector_store import save_chomadb

def process_files(files_paths=None, overwrite=False, chat_id=None):
    """
    Process files and save to vector database
    """
    try:
        if files_paths:
            documents = load_documents(files_paths)
        else:
            raise ValueError("Either files_path or directory_path must be provided.")
        
        chunks = text_spliter(documents)
        
        # Inject chat_id into metadata if provided
        if chat_id:
            for chunk in chunks:
                chunk.metadata["chat_id"] = str(chat_id)
        
        # Save to vector database
        save_chomadb(chunks, overwrite=overwrite)
    except Exception as e:
        print(f"Error processing files: {e}")
        return False, str(e)
    return True, "Files processed and saved to vector database successfully."
