from fastapi import FastAPI, HTTPException, Body, Query, WebSocket, WebSocketDisconnect
import json
from typing import List
from app.database import engine, SessionLocal
from app import crud, models, schemas
from app.websocket import ConnectionManager, MessageInChat

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


################################################################################
# User


# login user
@app.get("/log_in/}")
async def log_in_user(email: str, password: str):
    login = await crud.get_log_in_user(email=email, password=password)
    if login:
        return dict(status_code=200, message="Пользователь успешно авторизован")
    return dict(status_code=404, message="Введены неверные логин и пароль")


@app.post("/user")
async def post_create_user(data: schemas.UserCreate = Body(...)):
    postuser = await crud.create_user(data)
    if isinstance(postuser, dict) and "error" in postuser:
        raise HTTPException(status_code=400, detail=postuser["error"])
    return dict(status_code=200, message="Пользователь успешно зарегистрирован")


@app.get("/user/{user_id}")
async def get_user(user_id: str):
    profileinfo = await crud.get_user_by_user_id(user_id)
    if isinstance(profileinfo, dict) and "error" in profileinfo:
        raise HTTPException(status_code=400, detail=profileinfo["error"])
    return profileinfo


@app.put("/update_user/{user_id}")
async def update_user(user_id: str, data: schemas.UserUpdate = Body(...)):
    updateuser = await crud.update_user(data, user_id=user_id)
    if isinstance(updateuser, dict) and "error" in updateuser:
        raise HTTPException(status_code=400, detail=updateuser["error"])
    return dict(status_code=200, message="Пользователь успешно обновлен")


################################################################################

################################################################################
# Message


@app.post("/post_message")
async def post_add_message(data: schemas.MessageCreate = Body(...)):
    postmessage = await crud.add_message(data)
    if isinstance(postmessage, dict) and "error" in postmessage:
        raise HTTPException(status_code=400, detail=postmessage["error"])
    return dict(status_code=200, message="Сообщение успешно добавлено")


# Get for Messages
@app.get("/get_messages/{chat_id}")
async def get_messages(
    chat_id: str,
    page: int = Query(ge=1, default=1),
    size: int = Query(ge=20, le=100, default=20),
) -> list:
    offset_min, offset_max = await crud.pagination(page=page, size=size)
    filtered_data = await crud.get_messages(chat_id=chat_id)
    response = filtered_data[offset_min:offset_max]
    return {"MessageResponse": response}


################################################################################

################################################################################
# Chat


@app.post("/post_chat")
async def post_create_chat(data: schemas.DataForCreateChat = Body(...)):
    postchat = await crud.create_chat(data.chat)
    postmessage = await crud.add_message(data.message)
    if isinstance(postchat, dict) and "error" in postchat:
        raise HTTPException(status_code=400, detail=postchat["error"])
    if isinstance(postmessage, dict) and "error" in postmessage:
        raise HTTPException(status_code=400, detail=postmessage["error"])
    return dict(status_code=200, message="Chat created successfully")


@app.get("/open_chats/{user_id}")
async def get_chats(
    user_id: str,
    page: int = Query(ge=1, default=1),
    size: int = Query(ge=5, le=100, default=20),
) -> list:
    offset_min, offset_max = await crud.pagination(page=page, size=size)
    filtered_data = await crud.get_chats(user_id=user_id)
    response = filtered_data[offset_min:offset_max]
    return {"ChatResponse": response}


@app.delete("/chat_delete")
async def delete_chats(chat_ids: List[str] = Body(...)):
    delchats = await crud.del_chats(chat_ids)
    if isinstance(delchats, dict) and "error" in delchats:
        raise HTTPException(status_code=400, detail=delchats["error"])
    return dict(status_code=200, message="Все чаты успешно удалены")


################################################################################
# Anohterusers


@app.get("/user_for_choose/{user_id}")
async def get_users_for_choose(user_id: str):
    users = await crud.get_choose_user(user_id=user_id)
    return users


################################################################################
# Websocket


manager = ConnectionManager()


@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message_to_add = MessageInChat(
                message_id=message_data["message_id"],
                id_chat=message_data["id_chat"],
                id_sender=message_data["id_sender"],
                content=message_data["content"],
                time=message_data["time"],
                type=message_data["type"],
            )

            await crud.add_message(message_to_add)
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
