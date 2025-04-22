import subprocess

def dump_wincred():
    try:
        output = subprocess.check_output("cmdkey /list", shell=True).decode(errors="ignore")
        return output.splitlines()
    except Exception as e:
        return [f"[erro credencial] {e}"]
