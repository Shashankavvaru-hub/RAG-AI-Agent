import os
import json
import shutil
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.db.database import get_db, DBChat, DBMessage
from src.db.schemas import Chat, Message
from src.llm.llm_client import agent_executor
from src.utils.helpers import process_files
from src.vectordb.vector_store import delete_chat_data

router = APIRouter()

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.get("/api/chats/", response_model=List[Chat])
async def get_chats(db: Session = Depends(get_db)):
    chats = db.query(DBChat).all()
    chats_serialized = jsonable_encoder(chats)
    return JSONResponse(content=chats_serialized)

@router.post("/api/chats/new/")
async def new_chat(db: Session = Depends(get_db)):
    new_chat = DBChat(name="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return JSONResponse(content={"detail": "New chat created successfully.", "chat_id": new_chat.id})

@router.get("/api/chats/{chat_id}/messages/")
async def get_chat_messages(chat_id: int, db: Session = Depends(get_db)):
    messages = db.query(DBMessage).filter(DBMessage.chat_id == chat_id).all()
    messages_serialized = jsonable_encoder(messages)
    return JSONResponse(content=messages_serialized)

@router.put("/api/chats/{chat_id}/rename/")
async def rename_chat(chat_id: int, payload: dict, db: Session = Depends(get_db)):
    chat = db.query(DBChat).filter(DBChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
    
    chat.name = name
    db.commit()
    
    return JSONResponse(content={"detail": "Chat renamed successfully."})

@router.delete("/api/chats/{chat_id}/delete")
async def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(DBChat).filter(DBChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    db.query(DBMessage).filter(DBMessage.chat_id == chat_id).delete()
    db.delete(chat)
    db.commit()
    
    chat_folder = os.path.join(UPLOAD_FOLDER, str(chat_id))
    if os.path.exists(chat_folder):
        shutil.rmtree(chat_folder)
        
    delete_chat_data(chat_id)
    
    return JSONResponse(content={"detail": "Chat deleted successfully."})

@router.post("/api/chats/{chat_id}/send/")
async def send_chat_message(
    chat_id: str, 
    query: str = Form(default=""), 
    agent: bool = Form(default=False),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    if chat_id == 'newChat':
        new_chat = DBChat(name="New Chat")
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        chat_id = new_chat.id
    else:
        try:
            chat_id = int(chat_id)
            chat = db.query(DBChat).filter(DBChat.id == chat_id).first()
            if not chat:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat ID")
    
    files_paths = []
    files_message = ""
    if files:
        for file in files:
            if file.filename == "":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file name")
            if not file.filename.endswith(('.txt', '.pdf', '.docx')):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
            chat_folder = os.path.join(UPLOAD_FOLDER, str(chat_id))
            os.makedirs(chat_folder, exist_ok=True)
            file_path = os.path.join(chat_folder, file.filename)
            files_paths.append(file_path)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
  
        success, files_message = process_files(files_paths=files_paths, chat_id=chat_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=files_message)
        
        files_message = f"{files_message}: {', '.join([file.filename for file in files])}"
    
    user_message_body = query if query else "Files uploaded" if files else "Empty message"
    user_message = DBMessage(chat_id=chat_id, type="user", body=user_message_body)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    reasoning_steps = []
    if query and query != "":
        response = agent_executor(query_text=query, agent=agent, chat_id=chat_id)
        final_response = response['response']  
        if response['sources']:
            final_response += '\n\nSources:\n' + "\n".join(response['sources'])
        reasoning_steps = response['reasoning_steps']
        
    elif files:
        final_response = files_message
    else:
        final_response = "I received your message but it appears to be empty. How can I assist you?"
    
    agent_message = DBMessage(chat_id=chat_id, type="agent", body=final_response, reasoning_steps=json.dumps(reasoning_steps))
    db.add(agent_message)
    db.commit()
    db.refresh(agent_message)
    
    chat = db.query(DBChat).filter(DBChat.id == chat_id).first()
    
    return JSONResponse(content={
        'agent_response': {
            'id': agent_message.id,
            'type': agent_message.type,
            'body': agent_message.body,
            'reasoning_steps': reasoning_steps,
        },
        'chat_id': chat_id,
        'chat_name': chat.name
    })
