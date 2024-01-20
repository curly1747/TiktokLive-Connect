import subprocess

cmd = r"python main.py"

process = subprocess.Popen(cmd)
process.wait()
