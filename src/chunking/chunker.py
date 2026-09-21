from langchain.text_splitter import RecursiveCharacterTextSplitter

def text_spliter(documents):
    """split documents to chunks"""
    text_spliter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_spliter.split_documents(documents)
    # logging
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks
