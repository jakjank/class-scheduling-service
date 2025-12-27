import json

class Cluster:
    def __init__(self, range: list[int], groups_ids: list[int]):
        self.range = range
        self.groups_ids = groups_ids

    @staticmethod
    def from_json(json_string : str) -> 'Cluster':
        data = json.loads(json_string)
        range = data.get('range')
        ids = data.get('groups_ids')
        return Cluster(range, ids)