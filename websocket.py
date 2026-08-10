from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(
    self,
    username: str,
    websocket: WebSocket
    ):
        await websocket.accept()

        old_connection = self.active_connections.get(username)

        if old_connection:
            try:
                await old_connection.close()
            except Exception:
                pass

        self.active_connections[username] = websocket

        print(f"{username} connected")
        print("Online:", list(self.active_connections.keys()))

    def disconnect(
    self,
    username: str,
    websocket: WebSocket | None = None
    ):
 

        current = self.active_connections.get(username)

        if websocket is None or current is websocket:
            self.active_connections.pop(username, None)

        print(f"{username} disconnected")
        print("Online:", list(self.active_connections.keys()))

    def is_online(self, username: str) -> bool:
        return username in self.active_connections

    async def send_to_user(
        self,
        username: str,
        data: dict
    ) -> bool:

        websocket = self.active_connections.get(username)

        if not websocket:
            return False

        try:
            await websocket.send_json(data)
            return True

        except Exception:
            self.disconnect(username, websocket)
            return False

    def online_users(self) -> list[str]:
        return list(self.active_connections.keys())
