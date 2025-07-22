import asyncio
import websockets
import json
import time
import keyboard


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

async def get_rfid_input():
    card_id = ""
    print("Esperando lectura de RFID (escribe 'quit' o 'salir' para terminar)...")
    
    while True:
        try:
            
            event = keyboard.read_event(suppress=True)  
            if event.event_type == keyboard.KEY_DOWN:
                key = event.name
                
                if key in "0123456789":
                    card_id += key
                elif key == "enter":
                    if card_id:
                        
                        data = {
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "card_id": card_id
                        }
                        
                        if connected_clients:
                            for client in connected_clients:
                                await client.send(json.dumps(data))
                            print(f"Enviando: {data}")
                        else:
                            print("No hay clientes conectados.")
                        card_id = ""  
                elif key in ["q", "s"]:  
                    card_id += key
                    if card_id.lower() in ["quit", "salir"]:
                        print("Terminando el bucle de entrada...")
                        break
                    elif len(card_id) > 10:  
                        card_id = ""
        except Exception as e:
            print(f"Error al procesar entrada: {e}")
        await asyncio.sleep(0.01)  

async def main():
    
    server = await websockets.serve(send_data, "0.0.0.0", 8765)
    print("WebSocket server started on ws://localhost:8765")
    
    
    await asyncio.gather(get_rfid_input(), server.wait_closed())

if __name__ == "__main__":
    asyncio.run(main())