from fastapi import FastAPI

import users
import chat


app = FastAPI(
    title="Chat API",
    description="Simple FastAPI chat application",
    version="1.0.0"
   ) 


# =========================
# ROUTERS
# =========================

app.include_router(users.router)
app.include_router(chat.router)


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "Chat API is running"
    } 
