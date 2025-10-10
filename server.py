# server.py
import asyncio
import websockets

async def handle_connection(websocket, path):
    print("A client connected!")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            print(f"path: {path}")
            await websocket.send(f"Server received: {message}")
    except websockets.ConnectionClosed:
        print("A client disconnected")

async def main():
    async with websockets.serve(handle_connection, "localhost", 8080):
        print("WebSocket server is running on ws://localhost:8080")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())