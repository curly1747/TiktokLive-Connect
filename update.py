import subprocess
import ctypes
def alert(title, text, style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

cmd = "git pull origin master"

process = subprocess.Popen(cmd)
process.wait()

alert('Thông báo', 'Đã tải cập nhật mới nhất')
