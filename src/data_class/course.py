import json

class Course:
    def __init__(self, id : int, name : str):
        self.id = id
        self.name = name

    @staticmethod
    def from_json(json_string : str) -> 'Course':
        data = json.loads(json_string)
        id = data.get('id')
        name = data.get('name')
        return Course(id, name)