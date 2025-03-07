import sys
import socket
import web
import json
import logging
import time
import os
from keywin import keyboard, KeyCode


HOST = "0.0.0.0"
PORT = 2828

urls = ("/", "freedom")


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


if __name__ == "__main__":
    ip = get_ip()
    strat_key = ""
    strat_key_str = ""

    if not os.path.isfile("config.txt"):
        config = open("config.txt", "w+")
        strat_key_str = "VK_LCONTROL"
        config.write(json.dumps({"key": strat_key_str}))
        strat_key = getattr(KeyCode, strat_key_str)

    config = open("config.txt", "r+")
    config_json = json.loads(config.read())
    strat_key_str = config_json["key"]
    strat_key = getattr(KeyCode, strat_key_str)
    print("Changing stratagem key with --key VK_KEYNAME")
    print(
        "Find keyname with https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes"
    )

    print(f"Hellpad Terminal IP: {ip}")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--key":
            strat_key_str = sys.argv[2]
            strat_key = getattr(KeyCode, strat_key_str)
            config = open("config.txt", "w")
            config.write(json.dumps({"key": strat_key_str}))
    print(f'Stratagem key: "{strat_key_str}"')
    config.flush()
    config.close()


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
                if True:
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
    strat_key = ""

    def POST(self):
        if self.strat_key == "":
            with open("config.txt", "r+") as f:
                self.strat_key = getattr(KeyCode, json.loads(f.read())["key"])
        data = json.loads(web.data())
        key = data["key"]
        if data["is_first"]:
            keyboard.hold(self.strat_key)
        elif data["is_key"]:
            if key == "num2":
                keyboard.hold(KeyCode.VK_DOWN)
                print(f"{data["key"]}".replace("num", ""), end="")
            elif key == "num4":
                keyboard.hold(KeyCode.VK_LEFT)
                print(f"{data["key"]}".replace("num", ""), end="")
            elif key == "num6":
                keyboard.hold(KeyCode.VK_RIGHT)
                print(f"{data["key"]}".replace("num", ""), end="")
            elif key == "num8":
                keyboard.hold(KeyCode.VK_UP)
                print(f"{data["key"]}".replace("num", ""), end="")
        else:
            print(f" {data["text"]}")
            time.sleep(0.5)
            keyboard.release(self.strat_key)
        time.sleep(0.2)
        keyboard.release(KeyCode.VK_DOWN)
        keyboard.release(KeyCode.VK_UP)
        keyboard.release(KeyCode.VK_LEFT)
        keyboard.release(KeyCode.VK_RIGHT)
        return "freedom forever"


if __name__ == "__main__":
    print("Terminal start on ", end="")
    webapp = WebApplication(urls, globals())
    webapp.run(PORT, Log)
