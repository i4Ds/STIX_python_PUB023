#!/usr/bin/python3

def get_node_children(data,name):
    if isinstance(data,list):
        for e in data:
            if isinstance(e, dict):
                if e['name'] == name:
                    return e['children']
            elif isinstance(e, tupe):
                if e[0] == name:
                    return e[3]
    return None

def get_nodes(data, name):
    if not data:
        return None
    if isinstance(data,list):
        if isinstance(data[0], dict):
            return [element for element in data if element['name'] == name]
        elif isinstance(data[0], tuple): 
            return [element for element in data if element[0] == name]
    return None

def get_raw(data, name):
    if isinstance(data[0], dict):
        return [int(item['raw'][0]) for item in data if item['name']==name]
    elif isinstance(data[0], tuple): 
        return [int(item[1][0]) for item in data if item[0]==name]
    else:
        return []
def get_eng(data, name):
    if isinstance(data[0],dict):
        return [item['eng'] for item in data if item['name']==name]
    elif isinstance(data[0]) is tuple: 
        return [item[2] for item in data if item[0]==name]


