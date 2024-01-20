import os
from module.app import TikTokDance
from module.mixer import Mixer
from web import Webapp
import ctypes
import time


def alert(title, text, style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def is_installed(app):
    from shutil import which
    is_tool = which(app) is not None
    if is_tool:
        return True
    import winapps
    for item in winapps.list_installed():
        if app in item.name:
            return True
    return False


for app in ['redis-cli', 'VLC media player', 'python']:
    valid = is_installed(app)
    if not valid:
        alert('Lỗi', f"Vui lòng cài đặt '{app}' trong thư mục 'install' trước khi sử dụng")
        os._exit(1)

mixer = Mixer()
mixer.start()

tiktok_dance = TikTokDance(mixer=mixer)
web = Webapp(tiktok_dance=tiktok_dance, mixer=mixer)
web.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os._exit(2)
