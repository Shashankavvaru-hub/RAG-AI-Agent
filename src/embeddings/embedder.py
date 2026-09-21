import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def get_embedder():
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
