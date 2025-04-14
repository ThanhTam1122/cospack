#!/usr/bin/env python3
"""
Main entry point for the Shipping Application.
This will run the PyQt UI, which connects to the FastAPI backend.
"""

import sys
import os
import subprocess
import threading
import time
import argparse
import requests

# Make sure we can import from the app and ui directories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Shipping Application")
    parser.add_argument("--backend-url", default="http://localhost:8000/api", 
                        help="URL of the FastAPI backend")
    parser.add_argument("--no-backend", action="store_true", 
                        help="Don't start the backend server")
    return parser.parse_args()

def wait_for_backend(url, timeout=10, interval=0.2):
    """Poll the backend until it responds or times out."""
    start_time = time.time()

    while True:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("✅ Backend is up and running")
                return True
        except requests.RequestException:
            pass  # Ignore and retry

        if time.time() - start_time > timeout:
            print("❌ Timed out waiting for backend to start")
            return False

        time.sleep(interval)

def start_backend():
    """Start the FastAPI backend server in a thread and wait for it to be ready"""
    try:
        import uvicorn

        backend_thread = threading.Thread(
            target=lambda: uvicorn.run(
                "app.main:app", 
                host="0.0.0.0", 
                port=8000, 
                reload=False
            ),
            daemon=True
        )
        backend_thread.start()

        backend_ready = wait_for_backend("http://localhost:8000")
        return backend_ready
    except Exception as e:
        print(f"Error starting backend server: {e}")
        return False

def main():
    """Main application entry point"""
    args = parse_arguments()

    # Set environment variable for the backend URL
    os.environ["BACKEND_URL"] = args.backend_url

    # Start the backend if not disabled
    if not args.no_backend:
        if not start_backend():
            print("Failed to start backend server. Exiting.")
            sys.exit(1)

    # Import and start the UI
    from ui.main_window import main as start_ui
    start_ui()

if __name__ == "__main__":
    main()
