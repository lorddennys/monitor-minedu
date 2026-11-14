import os
import json
import urllib.request
# Añade aquí el resto de librerías o funciones que ya utilizaba tu monitor original

ARCHIVO_JSON = "normas_conocidas.json"

def cargar_normas_conocidas():
    """Carga el archivo JSON con las normas registradas previamente. 
    Si no existe, crea uno vacío para evitar errores."""
    if not os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []
    
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def guardar_normas_conocidas(normas):
    """Guarda la lista actualizada de normas en el archivo JSON."""
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(normas, f, ensure_ascii=False, indent=4)

def ejecutar_monitor():
    # 1. Cargar el registro previo
    conocidas = cargar_normas_conocidas()
    
    # 2. AQUÍ VA TU LÓGICA ACTUAL para consultar la web del MINEDU
    # (Por ejemplo, el código que extrae las nuevas normas del portal)
    nuevas_normas_detectadas = [] # Reemplaza o integra esto con tu lógica de búsqueda
    
    # 3. Validar si hay novedades
    if nuevas_normas_detectadas:
        # Añades las nuevas a tu lista y guardas
        conocidas.extend(nuevas_normas_detectadas)
        guardar_normas_conocidas(conocidas)
        print("Se detectaron y guardaron nuevas normas.")
    else:
        # Aseguramos que el archivo exista de todas formas para el control de Git
        if not os.path.exists(ARCHIVO_JSON):
            guardar_normas_conocidas(conocidas)
        print("No se encontraron nuevas normas en esta revisión.")

if __name__ == "__main__":
    ejecutar_monitor()
