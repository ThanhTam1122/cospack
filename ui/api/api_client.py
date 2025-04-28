import os
import requests
import time

class ApiClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("BACKEND_URL", "http://localhost:8000/api")
        print(f"======== Connecting to backend at: {self.base_url} ==========")

    def get_pickings(self, params):
        try:
            response = requests.get(f"{self.base_url}/pickings/", params=params or {})
            response.raise_for_status()
            time.sleep(1)  
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []

    def do_shipping(self, params):
        try:
            response = requests.post(f"{self.base_url}/carrier-selection/batch-select/", json=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return { "err_msg": f"{e}" }
