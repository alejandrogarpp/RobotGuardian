import requests

# URL del servidor local (IP de la Raspberry + nombre del canal "alerta")
url_servidor = "http://192.168.4.1/alerta"
mensaje = "¡Hola clase! 🤖 El Robot Guardian ha detectado movimiento."

def enviar_notificacion(texto):
    print("Enviando notificación local...")
    try:
        respuesta = requests.post(url_servidor, data=texto.encode('utf-8'))
        if respuesta.status_code == 200:
            print("✅ ¡Notificación enviada al móvil con éxito!")
        else:
            print(f"❌ Error HTTP: {respuesta.status_code}")
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")

enviar_notificacion(mensaje)