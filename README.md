# 🤖 Robot Guardián

¡Bienvenido al proyecto **Robot Guardián**! 
Este es un sistema de seguridad inteligente basado en Raspberry Pi que detecta rostros en tiempo real. Cuando el robot detecta un "intruso" (una cara), realiza las siguientes acciones:
1. Enciende un **LED rojo** (apaga el verde).
2. **Sigue el rostro** de la persona usando dos servomotores (Eje X y Eje Y).
3. Envía una **notificación de alerta** a tu teléfono mediante el servicio [ntfy.sh](https://ntfy.sh).

Adicionalmente, el robot levanta un servidor web local para que puedas ver lo que la cámara está enfocando en tiempo real desde cualquier navegador.

---

## 📁 Estructura del Proyecto

El código está organizado de manera modular para que sea fácil de mantener y modificar:

- `app.py`: Es el archivo principal. Levanta el servidor web con Flask y unifica el resto de módulos.
- `hardware.py`: Se encarga de toda la interacción física utilizando los pines GPIO (movimiento de los servomotores y encendido de LEDs).
- `vision.py`: Maneja la cámara y utiliza OpenCV para procesar la imagen y detectar rostros.
- `notifications.py`: Contiene la lógica para enviar una alerta HTTP a tu canal de ntfy.

---

## 🛠️ Requisitos de Hardware

Asegúrate de tener conectados los componentes en los pines correspondientes (numeración **BCM**):

- **LED Verde:** PIN 20
- **LED Rojo:** PIN 21
- **Servo Motor (Pan / Eje X):** PIN 17
- **Servo Motor (Tilt / Eje Y):** PIN 14
- **Cámara:** Compatible con Raspberry Pi / USB.

---

## 📦 Dependencias de Software

Este proyecto requiere las siguientes librerías de Python. Puedes instalarlas utilizando `pip`:

```bash
pip install opencv-python Flask requests RPi.GPIO
```
*(Nota: Asegúrate de tener instalado también los archivos de Haar Cascades de OpenCV en la ruta configurada en `vision.py`)*.

---

## 🚀 Cómo ejecutar el proyecto

1. Enciende tu Raspberry Pi y asegúrate de que todos los componentes estén bien conectados.
2. Abre un terminal y navega hasta la carpeta del proyecto.
3. Ejecuta el archivo principal:
   ```bash
   python app.py
   ```
   *(Si usas Python 3 por defecto en tu sistema, podría ser necesario ejecutar `python3 app.py`)*
4. Para ver la cámara en directo, abre un navegador web en cualquier dispositivo de tu red local y escribe la dirección IP de tu Raspberry Pi seguida del puerto 5000:
   ```
   http://<IP_DE_LA_RASPBERRY>:5000
   ```
   *(Ejemplo: `http://192.168.1.100:5000`)*

5. Para detener la ejecución de forma segura y apagar los componentes, pulsa `Ctrl + C` en la terminal.
