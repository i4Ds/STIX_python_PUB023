
def get_node_children(data,name):
    if type(data) is list:
        for e in data:
            if type(e) is dict:
                if e['name'] == name:
                    return e['children']
            elif type(e) is tupe:
                if e[0] == name:
                    return e[3]

    return None

def get_nodes(data, name):
    if not data:
        return None
    if type(data) is list:
        if type(data[0]) is dict:
            return [element for element in data if element['name'] == name]
        elif type(data[0]) is tuple: 
            return [element for element in data if element[0] == name]
    return None

def get_raw(data, name):
    if type(data[0]) is dict:
        return [int(item['raw'][0]) for item in data if item['name']==name]
    elif type(data[0]) is tuple: 
        return [int(item[1][0]) for item in data if item[0]==name]
    else:
        return []
def get_eng(data, name):
    if type(data[0]) is dict:
        return [item['eng'] for item in data if item['name']==name]
    elif type(data[0]) is tuple: 
        return [item[2] for item in data if item[0]==name]


