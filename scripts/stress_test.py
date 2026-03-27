# Sends rapid strokes to gateway to test under load
import asyncio
import websockets
import json
import random
import time

GATEWAY_WS = "ws://localhost:8000/ws"
NUM_CLIENTS = 5
STROKES_PER_CLIENT = 20
DELAY_BETWEEN_STROKES = 0.05  # 50ms

async def client(client_id: int):
    try:
        async with websockets.connect(GATEWAY_WS) as ws:
            print(f"[Client {client_id}] Connected")
            for i in range(STROKES_PER_CLIENT):
                stroke = {
                    "type": "stroke",
                    "x1": random.randint(0, 800),
                    "y1": random.randint(0, 600),
                    "x2": random.randint(0, 800),
                    "y2": random.randint(0, 600),
                    "color": random.choice(["#000000", "#e94560", "#4caf50", "#2196f3"]),
                    "width": random.randint(1, 8),
                }
                await ws.send(json.dumps(stroke))
                print(f"[Client {client_id}] Sent stroke {i+1}/{STROKES_PER_CLIENT}")
                await asyncio.sleep(DELAY_BETWEEN_STROKES)

            print(f"[Client {client_id}] Done")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")

async def main():
    print(f"Starting stress test with {NUM_CLIENTS} clients, "
          f"{STROKES_PER_CLIENT} strokes each...")
    start = time.time()
    await asyncio.gather(*[client(i+1) for i in range(NUM_CLIENTS)])
    elapsed = time.time() - start
    total = NUM_CLIENTS * STROKES_PER_CLIENT
    print(f"\nDone. Sent {total} strokes in {elapsed:.2f}s "
          f"({total/elapsed:.1f} strokes/sec)")

if __name__ == "__main__":
    asyncio.run(main())
    