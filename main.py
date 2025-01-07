import socket
import web
import sys
import json
import logging
import time
from ahk import AHK

ahk = AHK(executable_path="AutoHotkey64.exe")

HOST = "0.0.0.0"
PORT = 2828

INTERVAL = 0

urls = ("/", "freedom")


class Log:
    def __init__(self, xapp, logname="wsgi"):
        class _log:
            def __init__(self, xapp, logname="wsgi"):
                self.logger = logging.getLogger(logname)

            def ignore(self, s):
                if not all(
                    [
                        web.config.get("debug_http", False),
                        any(["- 200 OK" in s, "- 202 Accepted" in s]),
                    ]
                ):
                    return True
                return False

            def write(self, s):
                if s[-1] == "\n":
                    s = s[:-1]
                if s == "":
                    return
                if self.ignore(s):
                    return
                self.logger.debug(s)

        self.app = xapp
        self.f = _log(logname)

    def __call__(self, environ, start_response):
        environ["wsgi.errors"] = self.f
        return self.app(environ, start_response)


class WebApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ("0.0.0.0", port))


class freedom:
    def POST(self):
        data = json.loads(web.data())
        # if data["is_key"]:
        #     print(f"{data["key"]}".replace("num", ""), end="")
        #     pyautogui.press(f"{data["key"]}")
        # else:
        #     print(f" {data["text"]}")
        # # return "freedom"
        # if is_first:
        #     keyboard.hold(KeyCode.VK_NUMPAD0)

        key = data["key"]
        if data["is_first"]:
            ahk.key_down("lcontrol")
        elif data["is_key"]:
            if key == "num2":
                ahk.key_down("down")
                # keyboard.press(KeyCode.VK_DOWN)
                print(f"{data["key"]}".replace("num", ""), end="")
                # time.sleep(0.3)
                # keyboard.release(KeyCode.VK_DOWN)
            elif key == "num4":
                ahk.key_down("left")
                # keyboard.press(KeyCode.VK_LEFT)
                print(f"{data["key"]}".replace("num", ""), end="")
                # time.sleep(0.3)
                # # time.sleep(100)
                # keyboard.release(KeyCode.VK_LEFT)
            elif key == "num6":
                ahk.key_down("right")
                # keyboard.press(KeyCode.VK_RIGHT)
                print(f"{data["key"]}".replace("num", ""), end="")
                # time.sleep(0.3)
                # # time.sleep(100)
                # keyboard.release(KeyCode.VK_RIGHT)
            elif key == "num8":
                # keyboard.hold(KeyCode.VK_UP)
                ahk.key_down("up")
                print(f"{data["key"]}".replace("num", ""), end="")
                # time.sleep(0.3)
                # # time.sleep(100)
                # keyboard.release(KeyCode.VK_UP)
        else:
            print(f" {data["text"]}", end="")
            print(" released")
            time.sleep(0.5)
            ahk.key_up("lcontrol")
        time.sleep(0.2)
        ahk.key_up("down")
        ahk.key_up("up")
        ahk.key_up("left")
        ahk.key_up("right")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test:
        return test.connect_ex((HOST, PORT)) == 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        INTERVAL = 0.3
        print(f"default interval: {INTERVAL}")
    else:
        INTERVAL = float(sys.argv[1])
        print(f"interval: {INTERVAL}")

    webapp = WebApplication(urls, globals())
    webapp.run(PORT, Log)
