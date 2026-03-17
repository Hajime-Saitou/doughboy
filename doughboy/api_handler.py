# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
import requests
import json
import math
import time
import os

class notion_api_handler:
    def __init__(self, api_key:str, api_version:str = "2026-03-11", base_url:str = "https://api.notion.com/v1/"):
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

    def get(self, endpoint:str, params=None, headers:dict=None) -> dict:
        if not headers:
            headers = self.make_headers("application/json")

        response = requests.get(self.make_endpoint_url(endpoint), headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint:str, data:dict={}, headers:dict=None) -> dict:
        if not headers:
            headers = self.make_headers("application/json")

        response = requests.post(self.make_endpoint_url(endpoint), headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint:str, data:dict={}, headers:dict=None) -> dict:
        if not headers:
            headers = self.make_headers("application/json")

        response = requests.patch(self.make_endpoint_url(endpoint), headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint:str, headers:dict=None) -> bool:
        if not headers:
            headers = self.make_headers("application/json")

        response = requests.delete(self.make_endpoint_url(endpoint), headers=headers)
        response.raise_for_status()
        return response.status_code == 204

# https://developers.notion.com/docs/working-with-files-and-media
class file_uploader:
    def __init__(self, api_handler):
        self.api_handler:notion_api_handler = api_handler
        self.chunk_size:int = 20 * 1024 * 1024

    def get_upload_id(self, data={}):
        headers:dict = self.api_handler.make_headers()
        response = self.api_handler.post("file_uploads", data=data, headers=headers)
        return response["id"]
    
    def singlepart_upload(self, filename:str) -> dict:
        basefilename:str = os.path.basename(filename)
        upload_id:str = self.get_upload_id()

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

    def multipart_upload(self, filename:str) -> dict:
        basefilename:str = os.path.basename(filename)
        size_left_of_sending_size: int = os.path.getsize(filename)
        number_of_parts:int = math.ceil(size_left_of_sending_size / self.chunk_size)

        data = {
            "mode": "multi_part",
            "filename": basefilename,
            "number_of_parts": number_of_parts,
        }
        upload_id:str = self.get_upload_id(data)

        headers:dict = self.api_handler.make_headers()
        endpoint_url:str = self.api_handler.make_endpoint_url(f"file_uploads/{upload_id}/send")
        for part_number in range(1, number_of_parts + 1):
            with open(filename, "rb") as f:
                sending_size:int = self.chunk_size if size_left_of_sending_size >= self.chunk_size else size_left_of_sending_size
                files = {
                    "file": (basefilename, f.read(sending_size)),
                    "part_number": (None, str(part_number))
                }

                response = requests.post(endpoint_url, headers=headers, files=files)
                response.raise_for_status()
                size_left_of_sending_size -= sending_size
            time.sleep(0.5)
        else:
            self.upload_completed(upload_id)

        return { "file_upload": { "id": upload_id }, "name": basefilename }

    def upload_completed(self, upload_id:str):
        headers:dict = self.api_handler.make_headers()
        endpoint_url = f"file_uploads/{upload_id}/complete"
        self.api_handler.post(endpoint_url, headers=headers)

    def retrieve_upload(self, upload_id:str) -> dict:
        headers:dict = self.api_handler.make_headers()
        endpoint_url = f"file_uploads/{upload_id}"
        return self.api_handler.get(endpoint_url, headers=headers)

    def import_external_file(self, external_url:str, filename:str) -> dict:   
        data = {
            "mode": "external_url",
            "filename": filename,
            "external_url": external_url
        }
        upload_id:str = self.get_upload_id(data)

        retry_limit:int = 5
        retry_interval:int = 2
        for retry_count in range(1, retry_limit + 1):
            upload_info:dict = self.retrieve_upload(upload_id)
            if upload_info["status"] == "uploaded":
                return { "file_upload": { "id": upload_id }, "name": filename }

            if retry_count < retry_limit:
                time.sleep(retry_interval ** retry_count)

        raise TimeoutError("Import imcomplete. operation is timed out.")
