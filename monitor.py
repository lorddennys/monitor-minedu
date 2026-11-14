import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ARCHIVO_JSON = "normas_conocidas.json"

# Credenciales tomadas de forma segura desde GitHub Secrets
EMAIL_REMITENTE = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
EMAIL_DESTINATARIO = os.environ.get("EMAIL_DEST") or EMAIL_REMITENTE


def cargar_normas_conocidas():
    if not os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar_normas_conocidas(normas):
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(normas, f, ensure_ascii=False, indent=4)


def enviar_alerta_correo(nuevas_normas):
    if not EMAIL_REMITENTE or not EMAIL_PASSWORD:
        print("Faltan las variables de entorno EMAIL_USER o EMAIL_PASS. No se envió correo.")
        return

    asunto = f"Alerta MINEDU: {len(nuevas_normas)} nueva(s) norma(s) detectada(s)"
    cuerpo = "Se han detectado actualizaciones relevantes en el portal del MINEDU:\n\n"
    
    for norma in nuevas_normas:
        cuerpo += f"- {norma}\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMITENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Correo de alerta enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


def consultar_portal_minedu():
    # Integra aquí tu lógica actual de consulta/scraping al MINEDU.
    # Debe devolver una lista de strings o diccionarios con las normas encontradas.
    return []


def ejecutar_monitor():
    conocidas = cargar_normas_conocidas()
    encontradas = consultar_portal_minedu()

    nuevas = [n for n in encontradas if n not in conocidas]

    if nuevas:
        conocidas.extend(nuevas)
        guardar_normas_conocidas(conocidas)
        enviar_alerta_correo(nuevas)
        print(f"Se registraron {len(nuevas)} nuevas normas.")
    else:
        if not os.path.exists(ARCHIVO_JSON):
            guardar_normas_conocidas(conocidas)
        print("Sin novedades en esta ejecución.")


if __name__ == "__main__":
    ejecutar_monitor()
