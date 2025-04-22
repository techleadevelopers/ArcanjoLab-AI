import os
import sys
import ctypes
import subprocess

def is_admin():
    """Verifica se o processo atual tem privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_as_admin():
    """Reinicia o script com privilégios administrativos."""
    print("[🔐] Não está como administrador. Elevando privilégios...")
    script = os.path.abspath(sys.argv[0])

    # Usa powershell para elevar com admin
    params = " ".join([script] + sys.argv[1:])
    subprocess.call([
        'powershell',
        '-Command',
        f'Start-Process python "{params}" -Verb RunAs'
    ])
    sys.exit(0)

if __name__ == "__main__":
    if not is_admin():
        relaunch_as_admin()

    # Aqui você pode importar o WormGPT e executar
    print("[✅] Executando como administrador.")
    from agent_loop import run_agent
    run_agent()
