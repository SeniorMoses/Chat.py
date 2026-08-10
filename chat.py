from fastapi import (
APIRouter,
WebSocket,
WebSocketDisconnect,
Depends
)
from sqlalchemy.orm import Session

from db import get_db
from auth import decode_token
from websocket import ConnectionManager
from models import Message, User

router = APIRouter(
prefix="/chat",
tags=["Chat"]
)

manager = ConnectionManager()

@router.websocket("/ws")
async def chat(
websocket: WebSocket,
token: str,
db: Session = Depends(get_db)
):

# Authenticate WebSocket user
    try:

        user = decode_token(
            token,
            db
        )

    except Exception as e:

        await websocket.close(
        code=1008
        )

        print(f"WebSocket authentication failed: {e}")

        return

    username = user.username

    await manager.connect(
    username,
    websocket
    )

    await websocket.send_json({
    "type": "connected",
    "username": username,
    "message": "Connected to chat"
    })

    try:

        while True:

            data = await websocket.receive_json()

            target_username = data.get("to")
            message_text = data.get("message")

        # -------------------------
        # Validate recipient
        # -------------------------

            if not target_username:

                await websocket.send_json({
                    "type": "error",
                    "message": "Recipient is required"
                })

                continue

        # -------------------------
        # Validate message
        # -------------------------

            if not message_text:

                await websocket.send_json({
                "type": "error",
                "message": "Message cannot be empty"
                })

                continue

            message_text = message_text.strip()

            if not message_text:

                await websocket.send_json({
                    "type": "error",
                    "message": "Message cannot be empty"
                })

                continue

            if len(message_text) > 2000:

                await websocket.send_json({
                "type": "error",
                "message": "Message is too long"
                })

                continue

        # -------------------------
        # Prevent self messaging
        # -------------------------

            if target_username == username:

                await websocket.send_json({
                    "type": "error",
                    "message": "You cannot send a message to yourself"
                })

                continue

        # -------------------------
        # Find recipient
        # -------------------------

            receiver = (
                db.query(User)
                .filter(
                     User.username == target_username
                )
                 .first()
            )

            if not receiver:

                await websocket.send_json({
                "type": "error",
                "message": "Recipient does not exist"
                })

                continue

        # -------------------------
        # Save message
        # -------------------------

            new_message = Message(
                 sender_id=user.id,
                receiver_id=receiver.id,
                message=message_text,
                is_read=False
            )

            db.add(new_message)
            db.commit()
            db.refresh(new_message)

        # -------------------------
        # Send to recipient
        # -------------------------

            delivered = await manager.send_to_user(
                target_username,
               {
                "type": "message",
                "id": new_message.id,
                "from": username,
                "to": target_username,
                "message": message_text,
                "is_read": False,
                "created_at": (
                        new_message.created_at.isoformat()
                        if new_message.created_at
                        else None
                    )
                }
            )

        # -------------------------
        # Tell sender result
        # -------------------------

            if delivered:

                await websocket.send_json({
                "type": "sent",
                "id": new_message.id,
                "to": target_username,
                "message": message_text,
                "delivered": True
                })

            else:

                await websocket.send_json({
                "type": "sent",
                "id": new_message.id,
                "to": target_username,
                "message": message_text,
                "delivered": False,
                "offline": True
            })

    except WebSocketDisconnect:

        manager.disconnect(
        username,
        websocket
    )

    except Exception as e:

        print(
        f"Chat error for {username}: {e}"
    )

        manager.disconnect(
            username,
            websocket
    )

@router.get("/online/{username}")
async def check_online(
username: str
):

    return {
    "username": username,
    "online": manager.is_online(username)
    }
 
@router.get("/online")
async def online_users():

    return {
    "online_users": manager.online_users()
    }
