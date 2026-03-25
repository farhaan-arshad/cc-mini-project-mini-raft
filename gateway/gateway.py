# FastAPI WebSocket server, leader routing, broadcast
import asyncio
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config ---
REPLICAS = [
    "http://replica1:8001",
    "http://replica2:8002",
    "http://replica3:8003",
]

# --- State ---
connected_clients: list[WebSocket] = []
current_leader: str | None = None


# --- Leader Discovery ---
async def find_leader():
    global current_leader
    async with httpx.AsyncClient(timeout=2.0) as client:
        for replica in REPLICAS:
            try:
                response = await client.get(f"{replica}/status")
                data = response.json()
                if data.get("state") == "LEADER":
                    current_leader = replica
                    print(f"[Gateway] Leader found: {current_leader}")
                    return
            except Exception:
                continue
    print("[Gateway] No leader found yet")
    current_leader = None


async def leader_probe_loop():
    while True:
        if current_leader is None:
            await find_leader()
        await asyncio.sleep(1.0)


# --- Startup ---
@app.on_event("startup")
async def startup():
    asyncio.create_task(leader_probe_loop())


# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"[Gateway] Client connected. Total: {len(connected_clients)}")
    try:
        while True:
            data = await websocket.receive_json()
            await forward_to_leader(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"[Gateway] Client disconnected. Total: {len(connected_clients)}")


# --- Forward Stroke to Leader ---
async def forward_to_leader(stroke: dict):
    global current_leader
    if current_leader is None:
        await find_leader()
        if current_leader is None:
            print("[Gateway] No leader available, dropping stroke")
            return
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                f"{current_leader}/client-stroke",
                json=stroke
            )
            if response.status_code != 200:
                print(f"[Gateway] Leader rejected stroke: {response.status_code}")
    except Exception as e:
        print(f"[Gateway] Leader unreachable: {e}, searching for new leader...")
        current_leader = None
        await find_leader()


# --- Broadcast Committed Stroke to All Clients ---
@app.post("/broadcast")
async def broadcast(stroke: dict):
    disconnected = []
    for client in connected_clients:
        try:
            await client.send_json(stroke)
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        connected_clients.remove(client)
    return {"status": "broadcasted", "clients": len(connected_clients)}


# --- Health Check ---
@app.get("/health")
async def health():
    return {"status": "ok", "leader": current_leader, "clients": len(connected_clients)}