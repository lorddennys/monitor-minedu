import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
from bs4 import BeautifulSoup

ARCHIVO_JSON = "normas_conocidas.json"

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


def enviar_reporte_correo(nuevas_normas, total_encontradas):
    if not EMAIL_REMITENTE or not EMAIL_PASSWORD:
        raise ValueError("ERROR CRÍTICO: El script no recibió EMAIL_USER o EMAIL_PASS desde GitHub Actions. Revisa el archivo .yml.")

    if nuevas_normas:
        asunto = f"🚨 MINEDU: {len(nuevas_normas)} nueva(s) norma(s) detectada(s)"
        cuerpo = "Se han encontrado las siguientes normas legales NUEVAS en el portal del MINEDU:\n\n"
        for norma in nuevas_normas:
            cuerpo += f"• {norma}\n"
    else:
        asunto = "✅ Reporte MINEDU: Revisión completada (Sin novedades)"
        cuerpo = (
            "El monitor se ejecutó correctamente, pero no se publicaron normas nuevas desde la última revisión.\n\n"
            f"Total de normas verificadas en el portal: {len(total_encontradas)}\n"
        )

    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMITENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    # Sin try/except silencioso: si Gmail rechaza algo, GitHub te lo mostrará claramente
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.send_message(msg)
    
    print(f"Correo enviado exitosamente a {EMAIL_DESTINATARIO}.")


def consultar_portal_minedu():
    # MANTÉN AQUÍ TU CÓDIGO DE SCRAPING REAL QUE YA ESTÁ EXTRAYENDO LAS NORMAS
    url = "https://www.gob.pe/institucion/minedu/normas-legales"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    normas = []
    for item in soup.find_all("a"):
        texto = item.get_text(strip=True)
        if "MINEDU" in texto and len(texto) > 15:
            normas.append(texto)
    return list(dict.fromkeys(normas))


def ejecutar_monitor():
    conocidas = cargar_normas_conocidas()
    encontradas = consultar_portal_minedu()

    nuevas = [n for n in encontradas if n not in conocidas]

    if nuevas:
        conocidas.extend(nuevas)
        guardar_normas_conocidas(conocidas)
        print(f"Se guardaron {len(nuevas)} nuevas normas.")
    else:
        if not os.path.exists(ARCHIVO_JSON):
            guardar_normas_conocidas(conocidas)
        print("Sin normas nuevas.")

    # Se envía el correo SIEMPRE, haya o no haya novedades
    enviar_reporte_correo(nuevas, encontradas)


if __name__ == "__main__":
    ejecutar_monitor()
