import asyncio
import websockets
import json
import time
from evdev import InputDevice, categorize, ecodes


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
    
    device_path = "/dev/input/event19"  

    try:
        device = InputDevice(device_path)
        print(f"Conectado al dispositivo: {device.name} ({device_path})")

        card_id = ""
        async for event in device.async_read_loop():
            if event.type == ecodes.EV_KEY:
                data = categorize(event)
                if data.keystate == 1:  
                    key = data.keycode
                    
                    if key.startswith("KEY_"):
                        char = key[4:].lower()  
                        if char in "0123456789":
                            card_id += char
                        elif key == "KEY_ENTER":
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
                        elif key in ["KEY_Q", "KEY_S"]:  
                            card_id += char
                            if card_id.lower() in ["quit", "salir"]:
                                print("Terminando el bucle de entrada...")
                                break
                            elif len(card_id) > 10:  
                                card_id = ""
            await asyncio.sleep(0.01)  

    except PermissionError as e:
        print(f"Error de permisos: {e}. Asegúrate de que el usuario tiene acceso a {device_path}.")
        print("Prueba agregar tu usuario al grupo 'input' o ejecuta el script con sudo.")
    except Exception as e:
        print(f"Error al leer el dispositivo: {e}")
    finally:
        if 'device' in locals():
            device.close()
            print("Dispositivo de entrada cerrado.")

async def main():
    
    server = await websockets.serve(send_data, "0.0.0.0", 8765)
    print("WebSocket server started on ws://localhost:8765")
    
    
    await asyncio.gather(get_rfid_input(), server.wait_closed())

if __name__ == "__main__":
    asyncio.run(main())