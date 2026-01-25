import json

class Cluster:
    def __init__(self, range : list[int], groups_ids : list[int]):
        if not all(isinstance(el, int) for el in range):
            raise ValueError(f"Field 'range' value in cluster must be a list of integers. Sent '{range}'.")
        self.range = range
        self.groups_ids = groups_ids

    @staticmethod
    def from_json(json_string : str) -> 'Cluster':
        REQUIRED_FIELDS = ['range', 'groups_ids']
        data = json.loads(json_string)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            missing_str = ", ".join(f"'{a}'" for a in missing)
            raise KeyError(f"Cluster is missing required fields: {missing_str}")
        range = data.get('range')
        ids = data.get('groups_ids')
        return Cluster(range, ids)
    