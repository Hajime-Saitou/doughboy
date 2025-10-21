# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
from doughboy.api_handler import *
import doughboy.props as props
import doughboy.prop_types as prop_types

class data_source_page:
    def __init__(self):
        self.payload:dict = None
        self.url = props.props("url", prop_types.url_prop)
        self.icon = props.props("icon", prop_types.icon_prop)
        self.parent_database_id:str = None
        self.parent_data_source_id:str = None

class data_source:
    __data_source_id__:str = None

    @classmethod
    def create_page_object(cls) -> data_source_page:
        new_page_object:data_source_page = data_source_page()

        for property_name, property_value in cls.__dict__.items():
            if isinstance(property_value, props.props):
                setattr(new_page_object, property_name, property_value.property_type_class(property_name, {}))
        new_page_object.data_source_id = cls.__data_source_id__

        return new_page_object

class doughboy:
    def __init__(self, api_key:str):
        self.api_handler:api_handler = api_handler(api_key)
        self.selection_columns:list = None
        self.filter:dict = None

    def select_from(self, *args) -> object:
        return selector(self, *args)

    def __is_data_source_class(self, data_source_class:data_source) -> bool:
        return False if not data_source_class or not issubclass(data_source_class, data_source) else True

    def update_to(self, data_source_class:data_source) -> object:
        if not self.__is_data_source_class(data_source_class):
            raise ValueError("exactly one data_source_class is required")

        return updator(self, data_source_class)

    def delete_from(self, data_source_class:data_source) -> object:
        if not self.__is_data_source_class(data_source_class):
            raise ValueError("exactly one data_source_class is required")

        return deletor(self, data_source_class)

    def insert_into(self, data_source_class:data_source) -> object:
        if not self.__is_data_source_class(data_source_class):
            raise ValueError("exactly one data_source_class is required")

        return insertor(self, data_source_class)

    def __is_page_object(self, page_object) -> bool:
        return False if not page_object or not isinstance(page_object, data_source_page) else True

    def update_one(self, page_object:data_source_page=None) -> object:
        if not self.__is_page_object(page_object):
            raise ValueError("page_object is required")

        payload:dict = {
            "properties": {}
        }
        target_properties:dict = { key: value for key, value in page_object.__dict__.items() if isinstance(value, prop_types.prop_type_base) and value.value_updated }
        if not target_properties:   # all properties is up to date. skip update.
            if page_object.property_updated == False:
                return None
        else:
            for value in target_properties.values():
                if value.type_name not in [ "icon", "url" ]:
                    payload["properties"].update(value.to_dict())
                else:
                    payload["properties"].update(value.to_dict())

        response = self.api_handler.patch(f"pages/{page_object.id}", payload)
        [ setattr(value, "value_updated", False) for value in target_properties.values() ]
        return response

    def delete_one(self, page_object:data_source_page=None) -> object:
        if not self.__is_page_object(page_object):
            raise ValueError("page_object is required")

        payload:dict = {
            "id": page_object.id,
            "archived": True,
        }

        return self.api_handler.patch(f"pages/{page_object.id}", payload)

    def insert_one(self, page_object:data_source_page=None) -> object:
        if not self.__is_page_object(page_object):
            raise ValueError("page_object is required")

        payload:dict = {
            "parent": {
                "data_source_id": page_object.data_source_id,
            },
            "properties": {}
        }
        target_properties:dict = { key: value for key, value in page_object.__dict__.items() if isinstance(value, prop_types.prop_type_base) }
        if not target_properties:
            raise ValueError("page_object has no properties")

        for value in target_properties.values():
            if value.type_name not in [ "icon", "url" ]:
                payload["properties"].update(value.to_dict())
            else:
                payload["properties"].update(value.to_dict())

        response = self.api_handler.post("pages", payload)
        page_object.id = response.get("id")
        [ setattr(value, "value_updated", False) for value in target_properties.values() ]

        page_object.id = response["id"]
        page_object.parent_data_source_id= response["parent"]["data_source_id"]
        page_object.parent_database_id = response["parent"]["database_id"]
        page_object.payload = response
        return page_object

class accessor:
    def __init__(self, controller:doughboy):
        self.controller:doughboy = controller
        self.data_source_class:data_source = None

class selector(accessor):
    def __init__(self, controller:doughboy, *args):
        super().__init__(controller)
        self.data_source_class:data_source = None
        self.selection_properties:list = None
        self.filter:dict = None
        self.sorts:dict = None
        self.pickup_selection_properties(*args)

    def pickup_selection_properties(self, *args) -> None:
        if len(args) < 1:
            raise ValueError("at least one data_source_class is required")

        if isinstance(args[0], props.prop_descriptor):
            data_sources:set = (arg.property.data_source_class for arg in args)
            if len(data_sources) > 1:
                raise ValueError("all properties must belong to the same data_source_class")

            self.data_source_class = args[0].data_source_class
            self.selection_properties = [arg.property.__name__ for arg in args]
        elif issubclass(args[0], data_source):
            self.data_source_class = args[0]
            self.selection_properties = [prop.__name__ for prop in args[0].__dict__.values() if isinstance(prop, props.props)]
        else:
            raise ValueError("invalid properties selection arguments")

    def where(self, *args) -> accessor:
        if len(args) < 1:
            return self

        self.filter = args[0]
        return self

    def order_by(self, *args) -> accessor:
        if len(args) < 1:
            return self

        self.sorts = [ *args ]
        return self

    def exec(self, filter_title_properties=False) -> list:
        payload:dict = {}
        if self.filter:
            payload["filter"] = self.filter

        if self.sorts:
            payload["sorts"] = self.sorts

        pages = []
        while True:
            url = f"data_sources/{self.data_source_class.__data_source_id__}/query"
            if filter_title_properties:
                url += "?filter_properties[]=title"

            response = self.controller.api_handler.post(url, payload)
            pages.extend(response.get("results", []))
            if not response.get("has_more"):
                break

        new_page_objects:list = []
        for page in pages:
            new_page_object:data_source_page = data_source_page()
            new_page_object.id = page.get("id")
            new_page_object.payload = page
            new_page_object.parent_database_id = page["parent"]["database_id"]
            new_page_object.parent_data_source_id = page["parent"]["data_source_id"]
            new_page_object.url = page["url"]
            new_page_object.icon = page["icon"]

            for property_name, property_value in page["properties"].items():
                if property_name not in self.selection_properties:
                    continue

                property = self.data_source_class.__dict__.get(property_name)
                setattr(new_page_object, property_name, property.property_type_class(property_name, property_value))
            new_page_objects.append(new_page_object)

        return new_page_objects

class updator(accessor):
    def __init__(self, controller:doughboy, data_source_class:data_source):
        super().__init__(controller)
        self.data_source_class:data_source = data_source_class
        self.selector:selector = selector(controller, (data_source_class))

    def where(self, *args) -> accessor:
        if len(args) < 1:
            return self

        self.selector = self.selector.where(*args)
        return self

    def values(self, **kwargs) -> None:
        if len(kwargs) < 1:
            raise ValueError("at least one property is required")

        for page in self.selector.exec():
            self.update_page_object(page, **kwargs)
            self.controller.update_one(page)

    def update_page_object(self, page_object, **kwargs):
        for key, value in kwargs.items():
            if hasattr(page_object, key):
                property:object = getattr(page_object, key)
                if isinstance(property, prop_types.prop_type_base):
                    property.value = value
                else:
                    raise ValueError(f"{key} is not a property")
            else:
                raise ValueError(f"{key} is not a property of {self.data_source_class.__name__}")

class deletor(accessor):
    def __init__(self, controller:doughboy, data_source_class:data_source):
        super().__init__(controller)
        self.selector = selector(controller, (data_source_class))

    def where(self, *args) -> accessor:
        if len(args) < 1:
            return self

        self.selector = self.selector.where(*args)
        return self

    def exec(self) -> None:
        pages:list = self.selector.exec(filter_title_properties=True)
        [ self.controller.delete_one(page) for page in pages ]

class insertor(accessor):
    def __init__(self, controller:doughboy, data_source_class:data_source):
        super().__init__(controller)
        self.data_source_class:data_source = data_source_class

    def values(self, **kwargs) -> data_source_page:
        if len(kwargs) < 1:
            raise ValueError("at least one property is required")

        new_page_object:data_source_page = self.data_source_class.create_page_object()
        for key, value in kwargs.items():
            if hasattr(new_page_object, key):
                property:object = getattr(new_page_object, key)
                if isinstance(property, prop_types.prop_type_base):
                    property.value = value
                else:
                    raise ValueError(f"{key} is not a property")
            else:
                raise ValueError(f"{key} is not a property of {self.data_source_class.__name__}")

        self.controller.insert_one(new_page_object)
        return new_page_object
