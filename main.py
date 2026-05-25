import json
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import engine, Base, get_db
from Models import Message
import schemas
app = FastAPI(title="Real-Time Chat Application")
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}
    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]
    async def broadcast_to_room(self, message_data:dict, room_id: str) -> None:
        if room_id in self.active_connections:
            payload = json.dumps(message_data)
            for connection in self.active_connections[room_id]:
                await connection.send_text(payload)

manager = ConnectionManager()
@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/rooms/{room_id}/messages", response_model=List[schemas.MessageResponse])
async def get_room_messages(room_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Message).where(Message.room_id == room_id).order_by(Message.timestamp.asc())
    result = await db.execute(query)
    return result.scalars().all()

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, db: AsyncSession = Depends(get_db)):
    await manager.connect(websocket,room_id,db)
    try:
        while True:
            raw_data = await websocket.receive_text()
            incoming_json = json.loads(raw_data)
            validated_message = schemas.MessageCreate(
                roomid=room_id,
                sender=incoming_json.get("sender", "Anonymous"),
                content=incoming_json.get("content", ""),
            )
            db_message = Message(
                room_id=validated_message.room_id,
                sender=validated_message.sender,
                content=validated_message.content
            )
            db.add(db_message)
            await db.commit()
            await db.refresh(db_message)

            broadclast_payload = {
                "id": db_message.id,
                "room_id": db_message.room_id,
                "sender": db_message.sender,
                "content": db_message.content,
                "timestamp": db_message.timestamp.isoformat()
            }
            await manager.broadcast_to_room(broadclast_payload, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)