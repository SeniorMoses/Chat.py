from fastapi import FastAPI

from users import router as users_router
from chat import router as chat_router


app = FastAPI(
    title="Chat API",
    description="Simple FastAPI messaging application",
    version="1.0.0"
)


# =========================
# ROUTERS
# =========================

app.include_router(users)
app.include_router(chat)


# =========================
# HOMEPAGE
# =========================

@app.get("/")
async def homepage():

    return {
        "message": "Chat API is running",
        "status": "online",
        "endpoints": {
            "signup": "/users/signup",
            "signin": "/users/signin",

            "online_users": "/chat/online",
            "check_online": "/chat/online/{username}",

            "websocket": "/chat/ws?token=YOUR_ACCESS_TOKEN",

            "docs": "/docs"
        }
    }
