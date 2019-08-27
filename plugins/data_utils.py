def get_nodes(data, name):
    if type(data) is list:
        return [element for element in data if element['name'] == name]
    return None
def get_node_children(data,name):
    if type(data) is list:
        for e in data:
            if e['name'] == name:
                return e['children']
    return None
def get_raw(data, name):
    return [int(item['raw'][0]) for item in data if item['name']==name]
def get_eng_text(parameters, name):
    return [item['value'] for item in parameters if item['name']==name][0]

