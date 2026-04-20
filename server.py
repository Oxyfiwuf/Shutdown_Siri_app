# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Header, HTTPException
import os

app = FastAPI()

clients = {}

# 🔐 ключ (бери з Railway ENV)
API_KEY = os.environ.get("API_KEY", "my_super_secret_key")


# -----------------------------
# 🔐 перевірка ключа
# -----------------------------
def verify_key(auth_header: str):
    if not auth_header:
        raise HTTPException(status_code=401, detail="No auth header")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth format")

    token = auth_header.split(" ")[1]

    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# -----------------------------
# WebSocket (ПК підключаються)
# -----------------------------
@app.websocket("/ws/{pc_id}")
async def ws_endpoint(websocket: WebSocket, pc_id: str):
    await websocket.accept()
    clients[pc_id] = websocket

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.pop(pc_id, None)
    except:
        clients.pop(pc_id, None)


# -----------------------------
# HTTP (Siri → команда)
# -----------------------------
@app.get("/")
async def root():
    return {"status": "alive"}


@app.post("/send_command")
async def send_command(request: Request, authorization: str = Header(None)):
    # 🔐 перевірка ключа
    verify_key(authorization)

    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "invalid json"}

    command = data.get("command")
    minutes = int(data.get("minutes", 0))
    target = data.get("target", "all")

    if not command:
        return {"status": "error", "message": "no command"}

    if target == "all":
        targets = list(clients.keys())
    elif isinstance(target, list):
        targets = target
    else:
        targets = [target]

    payload = {
        "command": command,
        "minutes": minutes
    }

    dead = []

    for pc_id in targets:
        ws = clients.get(pc_id)
        if not ws:
            continue

        try:
            await ws.send_json(payload)
        except:
            dead.append(pc_id)

    for pc_id in dead:
        clients.pop(pc_id, None)

    return {"status": "ok", "targets": targets}


# -----------------------------
# Debug endpoint
# -----------------------------
@app.get("/clients")
async def get_clients(authorization: str = Header(None)):
    verify_key(authorization)
    return {"online": list(clients.keys())}