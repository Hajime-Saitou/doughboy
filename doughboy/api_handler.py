# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
import requests
import json

base_uri:str = "https://api.notion.com/v1/"
api_version:str = "2025-09-03"

class api_handler:
    def __init__(self, api_key:str):
        if not api_key:
            raise ValueError("API key is required")

        if api_key.startswith("secret_"):
            raise ValueError("Please use the new API key format.")

        if not api_key.startswith("ntn_"):
            raise ValueError("Invalid API key format")

        self.api_key:str = api_key
        self.headers:dict = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": api_version
        }

    def get(self, endpoint:str, params=None) -> dict:
        response = requests.get(f"{base_uri}{endpoint}", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint:str, data:dict) -> dict:
        response = requests.post(f"{base_uri}{endpoint}", headers=self.headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint:str, data:dict) -> dict:
        response = requests.patch(f"{base_uri}{endpoint}", headers=self.headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint:str) -> bool:
        response = requests.delete(f"{base_uri}{endpoint}", headers=self.headers)
        response.raise_for_status()
        return response.status_code == 204

