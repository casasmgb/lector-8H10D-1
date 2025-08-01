import asyncio
import websockets
import json
import time
from pynput import keyboard
from threading import Thread

connected_clients = set()
async def send_data(websocket):
    connected_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

class RFIDReader:
    def __init__(self, loop):
        self.card_id = ""
        self.listener = None
        self.loop = loop
    
    def on_press(self, key):
        try:
            
            if hasattr(key, 'char') and key.char in "0123456789":
                self.card_id += key.char
            
            elif key == keyboard.Key.enter:
                if self.card_id:
                    data = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "card_id": self.card_id
                    }
                    if connected_clients:
                        
                        asyncio.run_coroutine_threadsafe(self.send_to_clients(data), self.loop)
                        print(f"Enviando: {data}")
                    else:
                        print("No hay clientes conectados.")
                    self.card_id = ""
        except Exception as e:
            print(f"Error al procesar tecla: {e}")
    
    async def send_to_clients(self, data):
        for client in connected_clients.copy():
            try:
                await client.send(json.dumps(data))
            except Exception as e:
                print(f"Error enviando a cliente: {e}")
    
    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

async def main():
    loop = asyncio.get_running_loop()
    
    server = await websockets.serve(send_data, "0.0.0.0", 8765)
    print("WebSocket server started on ws://localhost:8765")
    
    rfid_reader = RFIDReader(loop)
    rfid_reader.start()
    
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())