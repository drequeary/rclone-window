"""
Project Name: Rclone Window
Description: Webview for running rclone web gui in own window.
Author: DeAndre Wilson
Original Release: May 04, 2026
License: Apache-2.0
GitHub: https://github.com/drequeary/rclone-window
"""
import urllib.parse
import sys
import webview
import ctypes
import tomllib
import tomli_w
import shlex
import subprocess
import pathlib
from pathlib import Path

if getattr(sys, 'frozen', False):
    # CONST when running as compiled .exe
    IS_EXE = True
    ROOT_PATH = Path(sys.executable).parent.resolve().as_posix() + "/"
    ENTRY_FILE = sys.executable
    FILENAME = Path(ENTRY_FILE).name
else:
    # CONST when running as python script
    IS_EXE = False
    ROOT_PATH = Path(__file__).parent.resolve().as_posix() + "/"
    ENTRY_FILE = Path(sys.argv[0]).resolve()
    FILENAME = ENTRY_FILE.name

CONFIG_FILENAME = "rclone-window.toml"
VERSION = "1.0"

def create_config():
    """Create a default configuration file if it doesn't exist."""
    if pathlib.Path(f"{ROOT_PATH}{CONFIG_FILENAME}").exists():
        return

    data = {
        "webgui": {
            "address": "127.0.0.1",
            "port": 3000,
            "user": "user",
            "pass": "password"
        },
        "rc": {
            "address": "127.0.0.1",
            "port": 2000,
            "user": "admin",
            "pass": "password"
        },
        "webview": {
            "port": 1000
        }
    }

    with open(f"{ROOT_PATH}{CONFIG_FILENAME}", "wb") as f:
        tomli_w.dump(data, f)

create_config()

def get_config():
    with open(f"{ROOT_PATH}{CONFIG_FILENAME}", "rb") as f:
        return tomllib.load(f)

config = get_config()
address = config["webgui"]["address"]
port = config["webgui"]["port"]
user = config["webgui"]["user"]
passwd = config["webgui"]["pass"]

rc_port = config["rc"]["port"]
rc_address = config["rc"]["address"]
rc_user = config["rc"]["user"]
rc_passwd = config["rc"]["pass"]

webview_port = config["webview"]["port"]

def url_decode(encoded_url: str) -> str:
    """Decode a percent-encoded URL."""
    return urllib.parse.unquote(encoded_url)

def url_encode(url: str) -> str:
    """Encode a URL using percent-encoding."""
    return urllib.parse.quote(url, safe='')

def get_screen_resolution():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def launch_rclone_web():
    """Launch the rclone web interface."""
    if passwd and user:
        auth = f"--user={user} --pass={passwd}"
    else:
        auth = ""

    rclone_command = f"rclone gui {auth} --api-addr 127.0.0.1:{rc_port} --addr={address}:{port} --no-open-browser --no-console -v"
    process = subprocess.Popen(shlex.split(rclone_command))
    pid = process.pid
    return pid

def main():
    rclone_process = launch_rclone_web()
    address_encoded = url_encode(f"http://{address}:{rc_port}")
    url = f"http://{address}:{port}/login?pass={passwd}&url={address_encoded}&user={user}"

    # Launch webview window.
    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.create_window(
        f"Rclone Window {VERSION}",
        url = url,
        http_port = webview_port,
        width = 1580,
        height = 1020,
        x = (get_screen_resolution()[0] - 1580) // 2,
        y = (get_screen_resolution()[1] - 1020) // 2,
        min_size=(1280, 720),
        confirm_close=False,
    )
    webview.start(debug=False, http_port=port)

    # Kill the rclone process when the webview is closed.
    subprocess.run(["taskkill", "/F", "/PID", str(rclone_process)])

main()