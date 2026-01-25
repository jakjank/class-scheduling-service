from . import Availability, Cluster
import json

class Group:
    def __init__(
            self,
            id : int,
            duration : int,
            capacity : int,
            availability : Availability,
            labels : list[list],
            teacher_ids : list[int],
            occurrence_desc : list[int]
            ):
        self.id = id
        if not isinstance(duration, int):
            raise ValueError(f"Field 'duration' value in Group must be an integer. Sent '{duration}'.")
        self.duration = duration
        if not isinstance(capacity, int):
            raise ValueError(f"Field 'capacity' value in Group must be an integer. Sent '{capacity}'.")
        self.capacity = capacity
        self.availability = availability
        if not Group.are_labels_valid(labels):
            raise ValueError(f"Labels '{labels}' passed to the Group with id={id} have incorrect format. Refer to the documentation.")
        self.labels = labels
        self.teacher_ids = teacher_ids
        self.occurrence_desc = occurrence_desc
        self.clusters = []

    @staticmethod
    def from_json(json_string : str) -> 'Group':
        REQUIRED_FIELDS = ['id', 'duration', 'capacity', 'availability']
        data = json.loads(json_string)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            missing_str = ", ".join(f"'{a}'" for a in missing)
            raise KeyError(f"Group is missing required fields: {missing_str}")
        
        id = data.get('id')
        duration = data.get('duration')
        capacity = data.get('capacity')
        availability_data = data.get("availability")
        avail = Availability.from_json(json.dumps(availability_data))
        labels = data.get('labels', [])
        teacher_ids = data.get('teacher_ids', [])
        occurrence_desc = data.get('occurrence_desc', [])
        return Group(id, duration, capacity, avail, labels, teacher_ids, occurrence_desc)
    
    def add_cluster(self, c: Cluster):
        self.clusters.append(c)

    def are_labels_valid(labels):
        # Must be a list
        if not isinstance(labels, list):
            return False

        # Empty list is allowed
        if labels == []:
            return True

        # If labels is not empty then some tag must exists in each internal list
        # TODO: maybe as list comprehension?
        for l1 in labels:
            if not isinstance(l1, list) or l1 == []:
                return False
            for l2 in l1:
                if not isinstance(l2, list) or l2 == []:
                    return False
                for tag in l2:
                    if not isinstance(tag, str):
                        return False
        return True
