from fastapi import WebSocket


class MessageInChat:
    def __init__(self, message_id: str, id_chat: str, id_sender: str, content: str, time: int, type: int):
        self.message_id = message_id
        self.id_chat = id_chat
        self.id_sender = id_sender
        self.content = content
        self.time = time
        self.type = type


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)