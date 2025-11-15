# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
import requests
import json
import os

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

    def make_headers(self, content_type=None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.api_version
        }
        if content_type:
            headers["Content-Type"] = content_type

        return headers

    def make_endpoint_url(self, endpoint:str) -> str:
        return f"{self.base_url}{endpoint}"

    def get(self, endpoint:str, params=None) -> dict:
        response = requests.get(self.make_endpoint_url(endpoint), headers=self.make_headers("application/json"), params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint:str, data:dict) -> dict:
        response = requests.post(self.make_endpoint_url(endpoint), headers=self.make_headers("application/json"), data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint:str, data:dict) -> dict:
        response = requests.patch(self.make_endpoint_url(endpoint), headers=self.make_headers("application/json"), data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint:str) -> bool:
        response = requests.delete(self.make_endpoint_url(endpoint), headers=self.make_headers("application/json"))
        response.raise_for_status()
        return response.status_code == 204

# https://developers.notion.com/docs/working-with-files-and-media
class file_uploader:
    def __init__(self, api_handler):
        self.api_handler:notion_api_handler = api_handler

    def get_upload_id(self):
        response = self.api_handler.post("file_uploads", {})
        return response["id"]

    def direct_upload(self, filename):
        upload_id:str = self.get_upload_id()
        basefilename = os.path.basename(filename)

        headers:dict = self.api_handler.make_headers()
        endpoint_url:str = self.api_handler.make_endpoint_url(f"file_uploads/{upload_id}/send")
        with open(filename, "rb") as f:
            files = {
                "file": (basefilename, f),
                "part_number": (None, "1")
            }

            response = requests.post(endpoint_url, headers=headers, files=files)
            response.raise_for_status()

        return { "file_upload": { "id": upload_id }, "name": basefilename }

    def multipart_upload(self, filename, number_of_part):
        pass

    def impoert_external_file(self, filename, external_url):
        pass
   
