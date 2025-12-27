import json
from .availability import Availability
from .record import Record

class Teacher:
    def __init__(self, id, name, quota, availability):
        self.id = id
        self.name = name
        self.quota = quota
        self.availability = availability

    @staticmethod
    def from_json(json_string):
        json_data = json.loads(json_string)
        availability_data = json_data.get("availability")
        if availability_data:
            avail = Availability(availability_data)
        else:
            avail = Availability()
            
        return Teacher(
            id=json_data.get('id'),
            name=json_data.get('name'),
            quota=json_data.get('quota'),
            availability = avail
        )
    
    def book_time_slot(self, day: str, hour: int, mask: list[int]) -> bool:
        return self.availability.remove(day, hour, mask)
