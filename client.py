# client.py
import websocket
import json
import time
import os
import threading
import socket
from winotify import Notification
from dotenv import load_dotenv

PC_ID = socket.gethostname()
load_dotenv()  # шукає файл .env в корені

SERVER_URL = os.getenv("SERVER_URL")

if not SERVER_URL:
    raise ValueError("⚠️ SERVER_URL не знайдено! Встанови в .env або в змінних Railway.")
SERVER_WS = f"wss://{SERVER_URL}/ws/{PC_ID}"

def show_notification(minutes):
    toast = Notification(
        app_id="Shutdown Controller",
        title="Вимкнення ПК",
        msg=f"Комп'ютер вимкнеться через {minutes} хв",
        duration="long"
    )

    toast.show()


def shutdown_pc(minutes):
    seconds = minutes * 60

    # показ повідомлення
    show_notification(minutes)

    # стандартний Windows shutdown (краще ніж sleep)
    os.system(f"shutdown /s /t {seconds}")


def cancel_shutdown():
    os.system("shutdown /a")

    toast = Notification(
        app_id="Shutdown Controller",
        title="Скасовано",
        msg="Вимкнення комп'ютера скасовано",
        duration="short"
    )
    toast.show()


def on_message(ws, message):
    try:
        data = json.loads(message)

        cmd = data.get("command")

        if cmd == "sleep":
            minutes = int(data.get("minutes", 0))
            shutdown_pc(minutes)

        elif cmd == "cancel":
            cancel_shutdown()

    except:
        pass


def on_close(ws, *args):
    time.sleep(5)
    start()


def on_open(ws):
    def keep_alive():
        while True:
            try:
                ws.send("ping")
                time.sleep(60)
            except:
                break

    threading.Thread(target=keep_alive, daemon=True).start()


def start():
    ws = websocket.WebSocketApp(
        SERVER_WS,
        on_message=on_message,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()


if __name__ == "__main__":
    time.sleep(120)
    start()