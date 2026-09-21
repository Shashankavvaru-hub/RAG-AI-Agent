import os

# Workaround for Python 3.9 SQLite limitation on Windows for ChromaDB
if os.name == 'nt':
    import ctypes
    dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sqlite3.dll')
    if os.path.exists(dll_path):
        ctypes.CDLL(dll_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
