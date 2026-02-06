from . import Availability
import json

class Room:
    def __init__(
            self,
            id : int,
            capacity : int,
            availability : Availability,
            labels : list[list]):
        self.id = id
        self.capacity = capacity
        if not isinstance(capacity, int):
            raise ValueError(f"Field 'capacity' value in Room must be an integer. Sent '{capacity}'.")
        self.availability = availability
        self.labels = labels

    @staticmethod
    def from_json(json_string : str) -> 'Room':
        REQUIRED_FIELDS = ['id', 'capacity', 'availability', 'labels']
        data = json.loads(json_string)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            req_fields_str = ", ".join(f"'{a}'" for a in missing)
            raise KeyError(f"Room is missing required fields: {req_fields_str}")
        
        id = data.get('id')
        capacity = data.get('capacity')
        availability_data = data.get("availability")
        availability = Availability.from_json(json.dumps(availability_data))
        labels = data.get('labels', [])
        
        return Room(id, capacity, availability, labels)
    
    def book_time_slot(self, day: str, slot: int, mask: list[int]) -> bool:
        return self.availability.remove(day, slot, mask)

    def satisfies_labels_DNF(self, labels_DNF: list[list[int]]) -> bool:
        for label_set in labels_DNF:
            if all(label in self.labels for label in label_set):
                return True
        return False
