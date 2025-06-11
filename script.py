import subprocess
import os
import signal
import sys
import time
import platform

# Конфигурация
APP_MODULE = "main:app"  # Формат: "файл:приложение"
UVICORN_CMD = [
    "uvicorn",
    APP_MODULE,
    "--reload",
    "--reload-dir=.",
    "--no-use-polling" if platform.system() != "Windows" else ""
]
PORT = 8000

class ServerManager:
    def __init__(self):
        self.process = None

    def start(self):
        """Запускает сервер."""
        print(f"🚀 Starting Uvicorn on http://localhost:{PORT}")
        self.process = subprocess.Popen(
            [arg for arg in UVICORN_CMD if arg],  # Фильтр пустых аргументов
            stdout=sys.stdout,
            stderr=sys.stderr,
            env={**os.environ, "PORT": str(PORT)},
            shell=True if platform.system() == "Windows" else False,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )

    def stop(self):
        """Останавливает сервер."""
        if self.process:
            print("\n🛑 Stopping Uvicorn...")
            if platform.system() == "Windows":
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()
            print("Server stopped.")

if __name__ == "__main__":
    server = ServerManager()
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"⚠️ Error: {e}")
        server.stop()