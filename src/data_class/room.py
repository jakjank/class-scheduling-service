import json
from .availability import Availability
from .record import Record

class Room:
    def __init__(self, id:int, capacity:int, availability:Availability, labels:list[list]):
        self.id = id
        self.capacity = capacity
        self.availability = availability
        self.labels = labels

    @staticmethod
    def from_json(json_string : str) -> 'Room':
        data = json.loads(json_string)
        id = data.get('id')
        capacity = data.get('capacity')
        
        availability_data = data.get("availability")
        if availability_data:
            availability = Availability(availability_data)
        else:
            availability = Availability()

        labels = data.get('labels', [])
        
        return Room(id, capacity, availability, labels)
    
    def book_time_slot(self, day: str, hour: int, mask: list[int]) -> bool:
        return self.availability.remove(day, hour, mask)
