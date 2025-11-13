# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
import requests
import json

class notion_api_handler:
    def __init__(self, api_key:str, api_version:str = "2025-09-03", base_url:str = "https://api.notion.com/v1/"):
        if not api_key:
            raise ValueError("API key is required")

        if api_key.startswith("secret_"):
            raise ValueError("Please use the new API key format.")

        if not api_key.startswith("ntn_"):
            raise ValueError("Invalid API key format")

        self.api_key:str = api_key
        self.api_version:str = api_version
        self.base_url:str = base_url

    def make_headers(self, content_type="application/json"):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": content_type,
            "Notion-Version": self.api_version
        }

    def make_endpoint_url(self, endpoint:str) -> str:
        return f"{self.base_url}{endpoint}"

    def get(self, endpoint:str, params=None) -> dict:
        response = requests.get(self.make_endpoint_url(endpoint), headers=self.make_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint:str, data:dict) -> dict:
        response = requests.post(self.make_endpoint_url(endpoint), headers=self.make_headers(), data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint:str, data:dict) -> dict:
        response = requests.patch(self.make_endpoint_url(endpoint), headers=self.make_headers(), data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint:str) -> bool:
        response = requests.delete(self.make_endpoint_url(endpoint), headers=self.make_headers())
        response.raise_for_status()
        return response.status_code == 204
