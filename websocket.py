import asyncio
import websockets
import json
import threading

connected_clients = set()

async def send_data(websocket):
    # agregar cliente
    connected_clients.add(websocket)
    try:
        # esto amntiene la conexion activa emientas se envian datos
        while True:
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        # en caso de termianr se elimina el cliente
        connected_clients.remove(websocket)

def get_user_input(loop):
    while True:
        user_input = input("ingrese los datos (quit / salir): ")
        if user_input.lower() == 'quit':
            break
        data = {
            "mensaje": user_input
        }
        # envio de datos a los clientes conectados.
        if connected_clients:
            for client in connected_clients:
                asyncio.run_coroutine_threadsafe(
                    client.send(json.dumps(data)), loop
                )
            print(f"Enviando: {data}")
        else:
            print("No hay clientes conectados.")

async def main():
    loop = asyncio.get_running_loop()
    server = await websockets.serve(send_data, "0.0.0.0", 8765)
    print("WebSocket server started on ws://localhost:8765")
    
    # inicair el loop para enviar hasta que le progrma termine
    input_thread = threading.Thread(
        target=get_user_input, 
        args=(loop,), 
        daemon=True
    )
    input_thread.start()
    
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())