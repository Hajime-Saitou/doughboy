# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
import urllib

class prop_type_base:
    def __init__(self, name:str, payload:dict={}):
        self.name:str = name
        self.payload:dict = payload
        self.value_updated:bool = False

    @property
    def value(self) -> dict:
        raise NotImplementedError("Subclasses must implement value property")

    @value.setter
    def value(self, val) -> None:
        raise NotImplementedError("Subclasses must implement value setter")

    @property
    def default_value(self) -> dict:
        raise NotImplementedError("Subclasses must implement empty_value method")

    def to_dict(self) -> dict:
        return { self.name: self.payload }

class title_prop(prop_type_base):
    type_name:str = "title"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "title": [ { "type": "text", "text": { "content": "" }, "plain_text": "" } ] }
    
    @property
    def value(self) -> str:
        if "title" not in self.payload:
            self.payload.update(self.default_value)

        if len(self.payload["title"]) == 0:
            return None

        return "".join([ item["text"]["content"] for item in self.payload["title"] ])

    @value.setter
    def value(self, value) -> None:
        if value == self.value:
            return

        if value is None:
            self.payload["title"] = []
        else:
            if len(self.payload["title"]) == 0:
                self.payload.update(self.default_value)
            else:
                self.payload["title"] = self.payload["title"][:1]

            self.payload["title"][0]["text"]["content"] = value
            self.payload["title"][0]["plain_text"] = value
        self.value_updated = True

class rich_text_prop(prop_type_base):
    type_name:str = "rich_text"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)
   
    @property
    def default_value(self) -> dict:
        return { "rich_text": [ { "type": "text", "text": { "content": "" }, "plain_text": "" } ] }

    @property
    def value(self) -> str:
        if "rich_text" not in self.payload:
            self.payload.update(self.default_value)

        if len(self.payload["rich_text"]) == 0:
            return None

        return "".join([ item["text"]["content"] for item in self.payload["rich_text"] ])

    @value.setter
    def value(self, value) -> None:
        if value == self.value:
            return

        if value is None:
            self.payload["rich_text"] = []
        else:
            if len(self.payload["rich_text"]) == 0:
                self.payload.update(self.default_value)
            else:
                self.payload["rich_text"] = self.payload["rich_text"][:1]

            self.payload["rich_text"][0]["text"]["content"] = value
            self.payload["rich_text"][0]["plain_text"] = value
        self.value_updated = True

class date_prop(prop_type_base):
    type_name:str = "date"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "date": { "start": None, "end": None, "time_zone": None } }

    @property
    def value(self) -> dict:
        if "date" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["date"]

    @value.setter
    def value(self, values:dict) -> None:
        if values is None:
            if self.value is None:
                return

            self.payload["date"] = None
            self.value_updated = True
            return
        else:
            if self.value is not None:
                if not set(values) ^ set(self.value):
                    return

            self.payload.update(self.default_value)

        if "start" in values:
            self.start = values["start"]

        if "end" in values:
            self.end = values["end"]

        if "time_zone" in values:
            self.time_zone = values["time_zone"]

    def __normalize_payload(self):
        if self.start is None:
            if self.end is None and self.time_zone is None:
                self.payload["date"] = None
                return
            
            raise ValueError("must set property 'start', if configure property 'end' or 'time_zone'.")

    @property
    def start(self) -> str:
        if "date" not in self.payload or self.payload["date"] is None:
            self.payload.update(self.default_value)

        return self.payload["date"]["start"]

    @start.setter
    def start(self, value:str) -> None:
        if value == self.start:
            return

        self.payload["date"]["start"] = value
        self.__normalize_payload()
        self.value_updated = True

    @property
    def end(self) -> str:
        if "date" not in self.payload or self.payload["date"] is None:
            self.payload.update(self.default_value)

        return self.payload["date"]["end"]

    @end.setter
    def end(self, value:str) -> None:
        if value == self.end:
            return

        self.payload["date"]["end"] = value
        self.__normalize_payload()
        self.value_updated = True

    @property
    def time_zone(self) -> str:
        if "date" not in self.payload or self.payload["date"] is None:
            self.payload.update(self.default_value)

        return self.payload["date"]["time_zone"]
    
    @time_zone.setter
    def time_zone(self, value:str) -> None:
        if value == self.value:
            return

        self.payload["date"]["time_zone"] = value
        self.__normalize_payload()
        self.value_updated = True

class number_prop(prop_type_base):
    type_name:str = "number"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "number": None }

    @property
    def value(self) -> float:
        if "number" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["number"]

    @value.setter
    def value(self, value:float) -> None:
        if value == self.value:
            return

        self.payload["number"] = value
        self.value_updated = True

class select_prop(prop_type_base):
    type_name:str = "select"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "select": None }

    @property
    def value(self) -> str:
        if "select" not in self.payload:
            self.payload.update(self.default_value)

        if self.payload["select"] is None:
            return None

        return self.payload["select"]["name"]

    @value.setter
    def value(self, value:str) -> None:
        if value == "":
            raise ValueError("null-string is can not set to property type 'select'.")

        if value == self.value:
            return

        if value is None:
            self.payload["select"] = None
            self.value_updated = True
            return

        if self.payload["select"] is None:
            self.payload["select"] = { "name": value }
        else:
            self.payload["select"].update({ "name": value })
        self.value_updated = True

class multi_select_prop(prop_type_base):
    type_name:str = "multi_select"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "multi_select": [] }

    @property
    def value(self) -> list:
        if "multi_select" not in self.payload:
            self.payload.update(self.default_value)

        if not self.payload["multi_select"]:
            return self.payload["multi_select"]

        return [ item["name"] for item in self.payload["multi_select"] ]

    @value.setter
    def value(self, values:list) -> None:
        if values is None:
            raise ValueError("None is can not set to property type 'multi_select'.")

        if not set(values) ^ set(self.value):
            return

        self.payload["multi_select"] = [ { "name": value } for value in values ]
        self.value_updated = True

    def replace(self, old_name, new_name):
        try:
            index = self.value.index(old_name)
            self.payload["multi_select"][index] = { "name": new_name }
            self.value_updated = True
        except:
            raise KeyError(f"multi-select name {old_name} is not in list.")

    def remove(self, name):
        try:
            index = self.value.index(name)
            del self.payload["multi_select"][index]
        except Exception as e:
            raise KeyError(f"multi-select name {id} is not in list.")

    def append(self, name):
        self.payload["multi_select"].append({ "name": name })

class status_prop(prop_type_base):
    type_name:str = "status"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "status": None }

    @property
    def value(self) -> str:
        if "status" not in self.payload:
            self.payload.update(self.default_value)

        if self.payload["status"] is None:
            return None

        return self.payload["status"]["name"]

    @value.setter
    def value(self, value:str) -> None:
        if value == "":
            raise ValueError("null-string is can not set to property type 'status'.")

        if value == self.value:
            return

        if value is None:
            self.payload["status"] = None
            self.value_updated = True
            return

        self.payload["status"] = { "name": value }
        self.value_updated = True

class people_prop(prop_type_base):
    type_name:str = "people"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "people": [] }

    @property
    def value(self) -> list:
        if "people" not in self.payload:
            self.payload.update(self.default_value)

        return [ item["id"] for item in self.payload["people"] ]

    @value.setter
    def value(self, values:list) -> None:
        if values is None:
            raise ValueError("None is can not set to property type 'people'.")

        if not set(values) ^ set(self.value):
            return

        self.payload["people"] = [ { "id": value } for value in values ]
        self.value_updated = True

    def replace(self, old_id, new_id):
        try:
            index = self.value.index(old_id)
            self.payload["people"][index] = { "id": new_id }
            self.value_updated = True
        except Exception as e:
            raise KeyError(f"people id {old_id} is not in list.")

    def remove(self, id):
        try:
            index = self.value.index(id)
            del self.payload["people"][index]
        except Exception as e:
            raise KeyError(f"people id {id} is not in list.")

    def append(self, id):
        self.payload["people"].append({ "id": id })

class checkbox_prop(prop_type_base):
    type_name:str = "checkbox"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "checkbox": False }

    @property
    def value(self) -> bool:
        if "checkbox" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["checkbox"]

    @value.setter
    def value(self, value:bool) -> None:
        if value is None:
            raise ValueError("None is can not set to property type 'checkbox'.")

        if value == self.value:
            return

        self.payload["checkbox"] = value
        self.value_updated = True

class url_prop(prop_type_base):
    type_name:str = "url"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "url": None }

    @property
    def value(self) -> str:
        if "url" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["url"]

    @value.setter
    def value(self, value:str) -> None:
        if value == "":
            raise ValueError("null-string is can not set to property type 'url'.")

        if value == self.value:
            return

        self.payload["url"] = value
        self.value_updated = True

class email_prop(prop_type_base):
    type_name:str = "email"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "email": None }

    @property
    def value(self) -> str:
        if "email" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["email"]

    @value.setter
    def value(self, value:str) -> None:
        if value == "":
            raise ValueError("null-string is can not set to property type 'email'.")

        if value == self.value:
            return

        self.payload["email"] = value
        self.value_updated = True

class phone_number_prop(prop_type_base):
    type_name:str = "phone_number"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "phone_number": None }

    @property
    def value(self) -> str:
        if "phone_number" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["phone_number"]

    @value.setter
    def value(self, value:str) -> None:
        if value == "":
            raise ValueError("null-string is can not set to property type 'phone_number'.")

        if value == self.value:
            return

        self.payload["phone_number"] = value
        self.value_updated = True

class relation_prop(prop_type_base):
    type_name:str = "relation"

    def __init__(self, name:str, payload:dict={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "relation": [] }

    @property
    def value(self) -> list:
        if "relation" not in self.payload:
            self.payload.update(self.default_value)

        return [ item["id"] for item in self.payload["relation"] ]

    @value.setter
    def value(self, values:list) -> None:
        if values is None:
            raise ValueError("None is can not set to property type 'relation'.")

        if not set(values) ^ set(self.value):
            return

        self.payload["relation"] = [ { "id": value } for value in values ]
        self.value_updated = True

class file_prop(prop_type_base):
    type_name:str = "files"

    def __init__(self, name, payload={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "files": [] }

    def __make_file_check_list(self, values:list) -> list:
        items:list = []
        for value in values:
            for key, val in value.items():
                if key in [ "file", "external" ]:
                    items.append(f"{key}_{urllib.parse.quote(val['url'])}")
                elif key == "file_upload":
                    items.append(f"{key}_{val['id']}")

        return items

    @property
    def value(self) -> list:
        if "files" not in self.payload:
            self.payload.update(self.default_value)

        if len(self.payload["files"]) == 0:
            return []

        files:list = []
        for file in self.payload["files"]:
            if "file" in file:
                files.append({ "file": file["file"] })
            elif "external" in file:
                files.append({ "external": file["external"] })
            else:
                files.append({ "file_upload": file["file_upload"] })

        return files

    @value.setter
    def value(self, values:list) -> None:
        if values is None:
            raise ValueError("None is can not set to property type 'file'.")

        if not set(self.__make_file_check_list(values)) ^ set(self.__make_file_check_list(self.value)):
            return

        quoted_files:list = []
        for value in values:
            if "file" in value:
                if "url" not in value["file"]:
                    raise ValueError("ui uploaded file is must set url property.")
                
                value["file"]["url"] = urllib.parse.quote(value["file"]["url"])
            elif "external" in value:
                if "url" not in value["external"]:
                    raise ValueError("external file is must set url property.")

                value["external"]["url"] = urllib.parse.quote(value["external"]["url"])
            elif "file_upload" in value:
                if "id" not in value["file_upload"]:
                    raise ValueError("api uploaded file is must set id property.")
            else:
                raise ValueError(f"unknown file type: {value.keys()}.")

            quoted_files.append(value)

        self.payload["files"] = quoted_files
        self.value_updated = True

class icon_prop(prop_type_base):
    type_name:str = "icon"

    def __init__(self, name, payload={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "icon": None }

    @property
    def value(self) -> str:
        if "icon" not in self.payload:
            self.payload.update(self.default_value)

        if self.payload["icon"] is None:
            return None

        if "file" in self.payload["icon"]:
            return self.file
        elif "external" in self.payload["icon"]:
            return self.external

        return self.emoji

    @value.setter
    def value(self, value:dict) -> None:
        if value is None:
            if self.value is not None:
                self.value_updated = True
            self.payload["icon"] = None
            return

        if set(value) ^ set(self.value):
            return

        if "file" in value:
            self.file = value["file"]
        elif "eternal" in value:
            self.external = value["external"]
        elif "emoji" in value:
            self.emoji = value["emoji"]
        else:
            raise ValueError(f"unknown icon type: {value.keys()}.")

    @property
    def file(self) -> str:
        if "icon" not in self.payload:
            self.payload.update(self.default_value)

        if "file" not in self.payload["icon"]:
            return None

        return self.payload["icon"]["file"]["url"]

    @file.setter
    def file(self, value:str) -> None:
        if set(value) ^ set(self.file):
            return

        if value is None:
            self.payload["icon"] = None
            return
        
        self.payload["icon"].update({ "file": { "url": value } })
        self.value_updated = True

    @property
    def external(self) -> str:
        if "icon" not in self.payload:
            self.payload.update(self.default_value)

        if "external" not in self.payload["icon"]:
            return None

        return self.payload["icon"]["external"]["url"]

    @external.setter
    def external(self, value:str) -> None:
        if set(value) ^ set(self.external):
            return

        if value is None:
            self.payload["icon"] = None
            return
        
        self.payload["icon"].update({ "external": { "url": value } })
        self.value_updated = True

    @property
    def emoji(self) -> str:
        if "icon" not in self.payload:
            self.payload.update(self.default_value)

        if "emoji" not in self.payload["icon"]:
            return None

        return self.payload["icon"]["emoji"]

    @emoji.setter
    def emoji(self, value:str) -> None:
        if set(value) ^ set(self.emoji):
            return

        if value is None:
            self.payload["icon"] = None
            return
        
        self.payload["icon"].update({ "emoji": value })
        self.value_updated = True

class url_prop(prop_type_base):
    type_name:str = "url"

    def __init__(self, name, payload={}):
        super().__init__(name, payload)

    @property
    def default_value(self) -> dict:
        return { "url": None }

    @property
    def value(self) -> str:
        if "url" not in self.payload:
            self.payload.update(self.default_value)

        return self.payload["url"]

    @value.setter
    def value(self, value:dict) -> None:
        if value == self.value:
            return

        self.payload["url"] = value
        self.value_updated = True
