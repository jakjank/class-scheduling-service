from . import DAYS
import json

class Allocation:
    def __init__(
            self,
            group_id : int,
            room_ids : list[int],
            day : str,
            slot : int,
            ):
        self.group_id = group_id
        self.room_ids = room_ids
        if not day in DAYS:
            days_str = ", ".join(f"'{a}'" for a in DAYS)
            raise ValueError(f"Field 'day' value in Allocation must be one of: {days_str}. Sent '{day}'.")
        self.day = day
        if not isinstance(slot, int) or slot < 0:
            raise ValueError(f"Field 'slot' value in Allocation must be a non-negtive integer. Sent '{slot}'.")
        self.slot = slot

    @staticmethod
    def from_json(json_str: str) -> 'Allocation':
        REQUIRED_FIELDS = ['group_id', 'room_ids', 'day', 'slot']
        data = json.loads(json_str)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            missing_str = ", ".join(f"'{a}'" for a in missing)
            raise KeyError(f"Allocation is missing required fields: {missing_str}")
        
        group_id = data.get("group_id")
        room_ids = data.get("room_ids")
        day = data.get("day")
        slot = data.get("slot")
        
        return Allocation(group_id, room_ids, day, slot)

    def __repr__(self):
        return (
            f"Allocation("
            f"group_id={self.group_id}, "
            f"room_ids={self.room_ids}, "
            f"day={self.day}, "
            f"slot={self.slot}"
            f")"
        )
    
    def __eq__(self, value):
        if not isinstance(value, Allocation):
            return False
        
        return (self.group_id == value.group_id and
                self.room_ids == value.room_ids and
                self.day == value.day and
                self.slot == value.slot)
    