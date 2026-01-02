# Verwendung: python3 client.py 

import requests

class RemoteFile:
    def __init__(self, fs, name, mode):
        self.fs = fs
        self.name = name
        self.mode = mode
        self.buffer = ""
        self.closed = False
        if "r" in mode:
            self.buffer = self.fs.read_file(name)

    def read(self):
        if self.closed:
            raise IOError("Datei ist geschlossen")
        if "r" not in self.mode:
            raise IOError("Datei nicht im Lesemodus.")
        return self.buffer

    def write(self, content):
        if self.closed:
            raise IOError("Datei ist geschlossen")
        if "w" not in self.mode:
            raise IOError("Datei nicht im Schreibmodus")
        self.buffer = content

    def close(self):
        if self.closed:
            return
        if "w" in self.mode:
            self.fs.write_file(self.name, self.buffer)
        self.closed = True

class RemoteFileSystem:
    def __init__(self, server_url):
        self.server_url = server_url

    def listdir(self):
        r = requests.get(f"{self.server_url}/list")
        return r.json()

    def read_file(self, name):
        r = requests.get(f"{self.server_url}/read", params={"name": name})
        if r.status_code != 200:
            raise FileNotFoundError(f"Datei nicht gefunden: {name}")
        return r.text

    def write_file(self, name, content):
        r = requests.post(
            f"{self.server_url}/write",
            json={"name": name, "content": content})
        return r.text
    
    def delete_file(self, name):
        r = requests.delete(
            f"{self.server_url}/delete",
            json={"name": name})
        if r.status_code != 200:
            raise FileNotFoundError(f"Datei nicht gefunden: {name}")
        return True
    

    def open(self, filename, mode):
        return RemoteFile(self, filename, mode)


def mount(server_url):
    print(f"Mounte Dateisystem {server_url}...")
    return RemoteFileSystem(server_url)


def interactive_shell(fs: RemoteFileSystem):
    print("\nNFShell (Ctrl+C zum abbrechen")
    print("Befehle: ls, read <file>, write <file>, delete <file>, quit\n")

    while True:
        try:
            cmd = input("> ").strip().split()
            if not cmd:
                continue

            if cmd[0] in ("quit", "exit"):
                print("Programm wird beendet.")
                break

            elif cmd[0] == "ls":
                print("Shared:", fs.listdir())

            elif cmd[0] == "read":
                if len(cmd) < 2:
                    print("Verwendung: read <filename>")
                    continue
                f = fs.open(cmd[1], "r")
                print(f.read())
                f.close()

            elif cmd[0] == "write":
                if len(cmd) < 2:
                    print("Verwendung: write <filename>")
                    continue
                text = input("Text eingeben: ")
                f = fs.open(cmd[1], "w")
                f.write(text)
                f.close()
                print("Gespeichert.")

            elif cmd[0] == "delete":
                if len(cmd) < 2:
                    print("Verwendung: delete <filename>")
                    continue
                fs.delete_file(cmd[1])
                print("Geloescht.")

            else:
                print("Unbekannter Befehl.")

        except KeyboardInterrupt:
            print("\nProgramm wird beendet.")
            break
        except Exception as e:
            print("Fehler:", e)

fs = mount("http://127.0.0.1:5000")
interactive_shell(fs)

