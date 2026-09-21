from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, UnstructuredMarkdownLoader

def load_documents(files_paths: list):
    """load files"""
    documents = []
    for file_path in files_paths:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.md'):
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_path.endswith('.txt'):
            # Try with UTF-8 encoding first, fallback to other encodings if needed
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
            except UnicodeDecodeError:
                # Try with latin-1 
                try:
                    loader = TextLoader(file_path, encoding='latin-1')
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file_path}: {str(e)}")
                    continue
            continue  
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        documents.extend(loader.load())
    
    print(f"Loaded {len(documents)} documents from {len(files_paths)} files.")
    return documents
