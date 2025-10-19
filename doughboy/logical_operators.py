# doughboy
# https://github.com/Hajime-Saitou/doughboy
#
# Copyright (c) 2025 Hajime Saito
# MIT License
def or_(*filters) -> dict:
    return { "or": [ filter for filter in filters ] }

def and_(*filters) -> dict:
    return { "and": [ filter for filter in filters ] }

def asc_(descriptor) -> dict:
    return { "property": descriptor.property.__name__, "direction": "ascending" }

def ascending(descriptor) -> dict:
    return asc_(descriptor)

def desc_(descriptor) -> dict:
    return { "property": descriptor.property.__name__, "direction": "descending" }

def descending(descriptor) -> dict:
    return desc_(descriptor)
