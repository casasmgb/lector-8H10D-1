import serial
import asyncio
import websockets
import threading
from pynput import keyboard

# Configuración
SERIAL_PORT = "/dev/ttyUSB0"  # Ajusta según tu sistema
BAUD_RATE = 9600

CARDS_DB = {
    "12345678": "Empleado 1",
    "87654321": "Empleado 2",
}

websocket_server = None

async def send_data(websocket, uid, person=None):
    person = person or CARDS_DB.get(uid, "Desconocido")
    data = {"uid": uid, "person": person}
    await websocket.send(str(data))
    print(f"Datos enviados: {data}")

async def handle_websocket(websocket, path):
    global websocket_server
    websocket_server = websocket
    print("Cliente WebSocket conectado")
    try:
        await websocket.wait_closed()
    finally:
        websocket_server = None

async def read_rfid():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Leyendo RFID desde {SERIAL_PORT}...")
        while True:
            uid = ser.readline().decode('ascii', errors='ignore').strip()
            if uid and len(uid) >= 8:
                print(f"UID detectado: {uid}")
                if websocket_server:
                    await send_data(websocket_server, uid)
    except Exception as e:
        print(f"Error en lectura RFID: {e}")

def on_key_press(key):
    global input_buffer
    try:
        if key == keyboard.Key.enter:
            if input_buffer and websocket_server:
                asyncio.create_task(send_data(websocket_server, input_buffer, "Usuario de prueba"))
                input_buffer = ""
        elif hasattr(key, 'char'):
            input_buffer += key.char
    except AttributeError:
        pass

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

async def main():
    global loop
    loop = asyncio.get_running_loop()
    
    # Inicia servidor WebSocket
    async with websockets.serve(handle_websocket, "0.0.0.0", 8765):
        print("Servidor WebSocket iniciado. Presiona 'T' + Enter para enviar datos manuales.")
        
        # Hilo para RFID (ejecutado en el event loop)
        rfid_task = asyncio.create_task(read_rfid())
        
        # Hilo para teclado (en segundo plano)
        keyboard_thread = threading.Thread(target=start_keyboard_listener)
        keyboard_thread.daemon = True
        keyboard_thread.start()
        
        await rfid_task  # Mantén el servidor activo

if __name__ == "__main__":
    input_buffer = ""
    asyncio.run(main())  # ✅ Corrección clave: Usa asyncio.run() para manejar el event loop