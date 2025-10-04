import asyncio
import logging
import json
import os
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Response, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import uvicorn
from asyncio import Queue
import uuid

# --- Configuration ---
script_dir = os.path.dirname(os.path.abspath(__file__))
web_ui_dir = os.path.join(script_dir, "web_ui")
db_path = os.path.join(script_dir, "laitis_compatible.db")
DATABASE_URL = f"sqlite:///{db_path}"

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    connect_key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- In-memory storage for long polling ---
client_queues: dict[str, Queue] = {}
# Эта очередь будет хранить задачи (Future/asyncio.Event) для каждого запроса, ожидающего ответа.
pending_replies: dict[str, asyncio.Event] = {}
# Эта очередь будет хранить сами ответы от клиента
reply_storage: dict[str, any] = {}

app = FastAPI()

# --- Helper Functions ---
def db_get_or_create_client(db: Session, key: str, email: Optional[str], device: Optional[str]):
    client = db.query(Client).filter(Client.connect_key == key).first()
    if client:
        user = db.query(User).filter(User.id == client.user_id).first()
        if user:
            logging.info(f"Client '{key}' for user '{user.username}' reconnected.")
            return
        else:
            logging.warning(f"Client record '{key}' exists but user was not found. Deleting stale client record.")
            db.delete(client)
            db.commit()
    username = email if email and email != '-' else device
    if not username:
        username = f"user_{key[:8]}"
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logging.info(f"Creating new user '{username}'")
        user = User(username=username, password="password")
        db.add(user)
        db.commit()
        db.refresh(user)
    logging.info(f"Creating new client with key '{key}' for user '{username}'")
    client = Client(connect_key=key, user_id=user.id)
    db.add(client)
    db.commit()

# --- Endpoints for C# Client and Web UI ---

@app.get("/connect")
async def handle_connect(request: Request, key: str, email: Optional[str] = None, device: Optional[str] = None, response: Optional[str] = Query(None, alias="response")):
    """
    Handles long polling connection from C# clients.
    Now also handles the client's reply.
    """
    logging.info(f"Client '{key}' is waiting for a command. Email: {email}, Device: {device}")
    
    db = SessionLocal()
    try:
        db_get_or_create_client(db, key, email, device)
    finally:
        db.close()

    # Проверяем, есть ли ответ от клиента в параметрах запроса
    if response is not None and key in pending_replies:
        logging.info(f"Received reply from client {key} via /connect: {response}")
        # Сохраняем ответ и сигнализируем ожидающему запросу
        reply_storage[key] = response
        pending_replies[key].set()
        # Возвращаем 204, так как ответ на этот запрос будет обработан другим эндпоинтом
        return Response(status_code=204)

    if key not in client_queues:
        client_queues[key] = Queue(maxsize=5)

    try:
        message = await asyncio.wait_for(client_queues[key].get(), timeout=25.0)
        logging.info(f"Dequeued and sending message to client {key}: {message}")
        client_queues[key].task_done()
        return JSONResponse(content=message)
    except asyncio.TimeoutError:
        logging.info(f"Long polling timeout for client {key}.")
        return Response(status_code=204)
    except asyncio.CancelledError:
        logging.info(f"Client {key} disconnected unexpectedly.")
        return Response(status_code=400)

@app.get("/send")
async def handle_send(key: str, phrase: str):
    """
    Receives a command and waits for a reply from the client via the next /connect request.
    """
    if key not in client_queues:
        logging.warning(f"Received command for disconnected client '{key}'. Storing and hoping it connects soon.")
        client_queues[key] = Queue(maxsize=5)

    if key in pending_replies and not pending_replies[key].is_set():
        raise HTTPException(status_code=429, detail="A command is already pending for this client. Please wait for the reply.")
    
    # Создаем asyncio.Event для ожидания ответа
    pending_replies[key] = asyncio.Event()

    # Это формат команды, который ожидает клиент
    api_request = {"R": 0, "V": phrase}
    
    if client_queues[key].full():
        logging.error(f"Queue for client {key} is full. Command '{phrase}' dropped.")
        del pending_replies[key]
        raise HTTPException(status_code=429, detail="Command queue for client is full.")
        
    await client_queues[key].put(api_request)
    
    logging.info(f"Enqueued command for client '{key}': '{phrase}' and waiting for reply...")
    
    try:
        # Ждем, пока клиент отправит следующий /connect с ответом
        await asyncio.wait_for(pending_replies[key].wait(), timeout=30.0)
        
        # Получаем ответ из хранилища
        response_from_client = reply_storage.get(key, "No reply received")
        logging.info(f"Received reply for client {key}: {response_from_client}")
        
        return JSONResponse(content={"response": response_from_client})
    except asyncio.TimeoutError:
        logging.error(f"Timeout waiting for reply from client {key} for command '{phrase}'.")
        return JSONResponse(content={"error": "Client did not reply in time"}, status_code=504)
    finally:
        # Очищаем хранилище и события, чтобы избежать утечек
        if key in pending_replies:
            del pending_replies[key]
        if key in reply_storage:
            del reply_storage[key]

# --- Static Files ---

@app.get("/")
def read_root():
    index_path = os.path.join(web_ui_dir, "index.html")
    if not os.path.exists(index_path):
        return Response("<h1>Web UI not found</h1>", status_code=404, media_type="text/html")
    return FileResponse(index_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=53875)