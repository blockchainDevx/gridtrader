import websockets
import asyncio
import json

async def main_logic():
    async with websockets.connect('ws://localhost:8080') as websocket:
        await websocket.

asyncio.get_event_loop().run_until_complete(main_logic())