import os
import sys
import time
import socket
import subprocess
import urllib.request
import webbrowser

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    local_ip = get_local_ip()
    print("=" * 65)
    print("  COLLEGE RAG CHATBOT - HOSTED NETWORK PRODUCTION SERVER  ")
    print("=" * 65)

    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    if sys.platform == "win32":
        python_exe = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    else:
        python_exe = os.path.join(backend_dir, "venv", "bin", "python")

    if not os.path.exists(python_exe):
        python_exe = sys.executable

    print(f"\n[1/2] Launching Backend API Server on 0.0.0.0:8000...")
    backend_cmd = [
        python_exe, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print("      Waiting for backend startup...")
    time.sleep(2)

    # Ensure frontend build
    dist_dir = os.path.join(frontend_dir, "dist")
    if not os.path.exists(dist_dir):
        print("\n[2/2] Building Frontend Production Bundle...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, shell=True)

    print("\n[2/2] Launching Hosted Web Application on 0.0.0.0:3000...")
    frontend_cmd = [
        sys.executable, "-m", "http.server", "3000",
        "--bind", "0.0.0.0",
        "--directory", dist_dir
    ]
    
    frontend_process = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    time.sleep(1)

    print("\n" + "=" * 65)
    print("  HOSTED & ACCESSIBLE ACROSS YOUR NETWORK!  ")
    print(f"  - Local Browser:   http://localhost:3000")
    print(f"  - Network Access:  http://{local_ip}:3000")
    print(f"  - Backend API:     http://{local_ip}:8000/api")
    print(f"  - Swagger API Docs: http://{local_ip}:8000/docs")
    print("  - Default Admin:   admin@college.edu / AdminPassword123!")
    print("=" * 65)

    try:
        webbrowser.open(f"http://localhost:3000")
    except Exception:
        pass

    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping hosted servers...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
