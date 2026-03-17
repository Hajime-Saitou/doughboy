# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
import inspect

class props:
    def __init__(self, property_name:str, property_type_class:object):
        self.__name__:str = property_name
        self.property_type_class:object = property_type_class

    def __get__(self, _, owner:object):
        return prop_descriptor(self, owner)

operator_property_type_map = {
    # ex.)
    # operator_name : [ property-type, ... ]

    # python operators
    "__ne__": [
        "checkbox",
        "date",
        "id",
        "number",
        "rich_text",
        "status",
        "title",
    ],
    "__eq__": [
        "checkbox",
        "date",
        "id",
        "number",
        "rich_text",
        "status",
        "title",
    ],
    "__gt__": [
        "date",
        "id",
        "number",
    ],
    "__ge__": [
        "date",
        "id",
        "number",
    ],
    "__lt__": [
        "date",
        "id",
        "number",
    ],
    "__le__": [
        "date",
        "id",
        "number",
    ],

    # notion api operators
    "after": [
    	"date",
    ],
    "any": [
        "rollup",
    ],
    "before": [
        "date",
    ],
    "contains": [
        "multi-select",
        "people",
        "relation",
        "rich_text",
        "select",
        "title",
    ],
    "does_not_contain": [
        "multi-select",
        "people",
        "relation",
        "rich_text",
        "select",
        "title",
    ],
    "does_not_equals": [
        "checkbox",
        "id",
        "number",
        "rich_text",
        "status",
        "title",
    ],
    "ends_with": [
        "rich_text",
        "title",
    ],
    "equals": [
        "checkbox",
        "date",
        "id",
        "number",
        "rich_text",
        "status",
        "title",
    ],
    "every": [
        "rollup",
    ],
    "greater_than": [
        "id",
        "number",
    ],
    "greater_than_or_equal_to": [
        "id",
        "number",
    ],
    "is_empty": [
        "date",
        "files",
        "multi-select",
        "number",
        "poeple",
        "relaton",
        "rich_text",
        "select",
        "status",
        "title",
   ],
    "is_not_empty": [
        "date",
        "files",
        "multi-select",
        "number",
        "poeple",
        "relaton",
        "rich_text",
        "select",
        "status",
        "title",
    ],
    "less_than": [
        "id",
        "number",
    ],
    "less_than_or_equal_to": [
        "id",
        "number",
    ],
    "next_month": [
        "date",
    ],
    "next_week": [
        "date",
    ],
    "next_year": [
        "date",
    ],
    "none": [
        "rollup",
    ],
    "on_or_after": [
        "date",
    ],
    "on_or_before": [
        "date",
    ],
    "past_month": [
        "date",
    ],
    "past_week": [
        "date",
    ],
    "past_year": [
        "date",
    ],
    "starts_with": [
        "rich_text",
        "title",
    ],
    "this_week": [
        "date",
    ],
}

operator_conversion_map = {
    "__ne__": "does_not_equal",
    "__eq__": "equals",
    "__gt__": "greater_than",
    "__ge__": "greater_than_or_equal_to",
    "__lt__": "less_than",
    "__le__": "less_than_or_equal_to",
}

class  prop_descriptor:
    def __init__(self, property:props, data_source_class:object):
        self.property:props = property
        self.data_source_class:object = data_source_class

    def set(self, value:str):
        return { self.property.__name__: value }

    # Generic operator call
    def __operator_call(self, operator:str, other:object):
        if self.property.property_type_class.type_name not in operator_property_type_map[operator]:
            raise ValueError(f"{operator} is not available for {self.property.property_type_class.type_name}")

        #replace python operators to notion api operators
        if operator in operator_conversion_map:
            if self.property.property_type_class.type_name == "date":
                if operator == "__gt__":
                    operator = "after"
                elif operator == "__ge__":
                    operator = "on_or_after"
                elif operator == "__lt__":
                    operator = "before"
                elif operator == "__le__":
                    operator = "on_or_before"
            else:
                operator = operator_conversion_map[operator]

        return {
            "property": self.property.__name__,
            self.property.property_type_class.type_name: {
                operator: other
            }
        }

    # python operators
    def __eq__(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def __ge__(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def __gt__(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def __le__(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def __lt__(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def __ne__(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    # notion api operators
    def after(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def any(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def before(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def contains(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def does_not_contain(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def does_not_equal(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def ends_with(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def equals(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def every(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def greater_than(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def greater_than_or_equal_to(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def is_empty(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, True)

    def is_not_empty(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, True)

    def less_than(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def less_than_or_equal_to(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def next_month(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})
    
    def next_week(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})
    
    def next_year(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})

    def none(self, other):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def on_or_after(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)

    def on_or_before(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def past_month(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})
    
    def past_week(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})
    
    def past_year(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})

    def starts_with(self, other:object):
        return self.__operator_call(inspect.currentframe().f_code.co_name, other)
    
    def this_week(self):
        return self.__operator_call(inspect.currentframe().f_code.co_name, {})
