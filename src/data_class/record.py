import json

class Record:
    def __init__(self, group_id, teachers_ids, rooms_ids, day, hour, period_mask=[]):
        self.group_id = group_id
        self.teachers_ids = teachers_ids
        self.rooms_ids = rooms_ids
        self.day = day
        self.hour = hour
        self.period_mask = period_mask

    @staticmethod
    def from_json(json_str: str) -> 'Record':
        data = json.loads(json_str)
        group_id = data.get("group_id")
        teachers_ids =  data.get("teachers_ids")
        rooms_ids = data.get("rooms_ids")
        day = data.get("time_day")
        hour = data.get("time_hour")
        return Record(group_id, teachers_ids, rooms_ids, day, hour)

    def __str__(self):
        return (
            f"Record("
            f"group_id={self.group_id}, "
            f"teachers={self.teachers_ids}, "
            f"rooms={self.rooms_ids}, "
            f"day='{self.day}', "
            f"hour={self.hour}"
            f")"
        )
    
    def __eq__(self, value):
        if not isinstance(value, Record):
            return False
        
        return (self.group_id == value.group_id and
                self.teachers_ids == value.teachers_ids and
                self.rooms_ids == value.rooms_ids and
                self.day == value.day and
                self.hour == value.hour and
                self.period_mask == value.period_mask)