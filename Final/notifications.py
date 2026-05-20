import time
import requests

CANAL_NTFY = "mi_robot_guardian_2026"
URL_NOTIF = f"https://ntfy.sh/{CANAL_NTFY}"
ultimo_envio = 0
INTERVALO_NOTIFICACION = 15

def enviar_alerta(mensaje):
    global ultimo_envio
    ahora = time.time()

    if ahora - ultimo_envio > INTERVALO_NOTIFICACION:
        try:
            requests.post(
                URL_NOTIF,
                data=mensaje.encode('utf-8'),
                headers={
                    "Title": "ALERTA GUARDIAN",
                    "Priority": "4",
                    "Tags": "robot,warning"
                },
                timeout=3
            )
            ultimo_envio = ahora
        except Exception as e:
            print(f"Error notificación: {e}")
