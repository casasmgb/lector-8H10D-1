## Compilar el proyecto

### Instalar dependencias
```bash
pip install websockets pynput
pip install asyncio
pip install pyinstaller
```
## Opcional Puedes cambiar el icono
reemplazando la imagen 

### Compilar el proyecto
```bash
pyinstaller --onefile --windowed --icon=icon.jpg --name RFIDReader websocket.win.py
```

El compilado se encuentra en la carpeta `dist`