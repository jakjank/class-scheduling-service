from . import DAYS
import json

class Allocation:
    def __init__(
            self,
            group_id : int,
            room_ids : list[int],
            day : int,
            slots : list[int],
            ):
        self.group_id = group_id
        self.room_ids = room_ids
        if not day in DAYS:
            days_str = ", ".join(f"'{a}'" for a in DAYS)
            raise ValueError(f"Field 'day' value in Allocation must be one of: {days_str}. Sent '{day}'.")
        self.day = day
        if not isinstance(slots, list) or not all(isinstance(slot, int) for slot in slots) or not all(slot >= 0 for slot in slots):
            raise ValueError(f"Field 'slots' value in Allocation must be a list of non-negtive integers. Sent '{slots}'.")
        self.slots = slots

    @staticmethod
    def from_json(json_str: str) -> 'Allocation':
        REQUIRED_FIELDS = ['group_id', 'room_ids', 'day', 'slots']
        data = json.loads(json_str)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            missing_str = ", ".join(f"'{a}'" for a in missing)
            raise KeyError(f"Allocation is missing required fields: {missing_str}")
        
        group_id = data.get("group_id")
        room_ids = data.get("room_ids")
        day = data.get("day")
        slots = data.get("slots")
        
        return Allocation(group_id, room_ids, day, slots)

    def __repr__(self) -> str:
        return (
            f"Allocation("
            f"group_id={self.group_id}, "
            f"room_ids={self.room_ids}, "
            f"day={self.day}, "
            f"slots={self.slots}"
            f")"
        )
    
    def __eq__(self, value) -> bool:
        if not isinstance(value, Allocation):
            return False
        
        return (self.group_id == value.group_id and
                self.room_ids == value.room_ids and
                self.day == value.day and
                self.slots == value.slots)
