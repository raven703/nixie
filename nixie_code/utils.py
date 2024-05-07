import json
def load_settings():
    with open('boot.ini', 'r') as file:
        return json.load(file)
    

        