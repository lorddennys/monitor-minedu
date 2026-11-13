import json
import os
import urllib.request
from datetime import datetime

URL_MINEDU = "https://www.gob.pe/institucion/minedu/normas-legales"
CACHE_FILE = "normas_conocidas.json"

def verificar():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consultando portal MINEDU...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    conocidas = []
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                conocidas = json.load(f)
            except:
                conocidas = []
    
    try:
        req = urllib.request.Request(URL_MINEDU, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        encontradas = []
        pos = 0
        while True:
            pos = html.find('class="font-semibold text-text-color', pos)
            if pos == -1:
                break
            frag = html[pos:pos+300]
            i1, i2 = frag.find('>'), frag.find('</')
            if i1 != -1 and i2 != -1:
                t = frag[i1+1:i2].strip()
                if t and t not in encontradas and len(t) > 10:
                    encontradas.append(t)
            pos += 1
            
        novedades = [n for n in encontradas if n not in conocidas]
        if novedades:
            print(f"¡Nuevas normas detectadas: {len(novedades)}")
            for n in novedades:
                print(f"- {n}")
                conocidas.append(n)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(conocidas, f, ensure_ascii=False, indent=2)
        else:
            print("No hay normas nuevas.")
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    verificar()
