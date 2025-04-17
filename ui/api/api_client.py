import os
import requests
import time

class ApiClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("BACKEND_URL", "http://localhost:8000/api")
        print(f"======== Connecting to backend at: {self.base_url} ==========")

    def get_pickings(self):
        try:
            response = requests.get(f"{self.base_url}/pickings/")
            response.raise_for_status()
            time.sleep(2)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []

    def do_shipping(self):
        try:
            response = requests.get(f"{self.base_url}/pickings/")
            response.raise_for_status()
            time.sleep(3)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []
