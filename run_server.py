import webbrowser
import time
import subprocess
import sys

url = "http://127.0.0.1:8000/docs"

# Start FastAPI server
subprocess.Popen([
    sys.executable, "-m", "uvicorn", "server:app", "--reload"
])

# Give server time to start
time.sleep(2)

# Open Swagger automatically
webbrowser.open(url)
