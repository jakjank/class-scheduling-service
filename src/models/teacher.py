from . import Availability
import json

class Teacher:
    def __init__(
            self,
            id : int,
            availability : Availability):
        self.id = id
        self.availability = availability

    @staticmethod
    def from_json(json_string):
        REQUIRED_FIELDS = ['id', 'availability']
        data = json.loads(json_string)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            missing_str = ", ".join(f"'{a}'" for a in missing)
            raise ValueError(f"Teacher is missing required fields: {missing_str}")
        
        availability_data = data.get("availability")
        avail = Availability.from_json(json.dumps(availability_data))
            
        return Teacher(
            id=data.get('id'),
            availability = avail
        )
    
    def book_time_slot(self, day: str, slot: int, mask: list[int]) -> bool:
        return self.availability.remove(day, slot, mask)
