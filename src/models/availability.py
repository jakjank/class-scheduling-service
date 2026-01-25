from dataclasses import field
from typing import Dict, List
import json

DAYS = [1, 2, 3, 4, 5, 6, 7]

class Availability:
    slots: Dict[str, List[int]] = field(default_factory=lambda: {day: [] for day in DAYS})
    taken_periods: Dict = field(default_factory=dict)

    def __init__(self, dir : dict, taken_periods = None):
        invalid_keys = set(dir.keys()) - set(DAYS)
        if invalid_keys:
            inv_keys_str = ", ".join(f"'{a}'" for a in invalid_keys)
            raise KeyError(f"Invalid keys in availability data: {inv_keys_str}")
        filtered = {}
        for day in DAYS:
            slots = dir.get(day, [])
            if not all(isinstance(slot, int) and 0 <= slot for slot in slots):
                raise ValueError(f"Slots in Availability must be non-negative integers. Sent '{slot}'.")
            filtered[day] = slots
        self.slots = filtered
        
        # Taken periods does not happen in practice since user can set occurence_desc only for Groups.
        # Taken periods are added to Teachers and Rooms availabilities via their book_time_slot() function
        if taken_periods is None:
            taken_periods = {}
        
        if taken_periods:
            for key, value in taken_periods.items():
                if not isinstance(key, tuple) or len(key) != 2:
                    raise ValueError(f"Invalid taken_periods key '{key}'. Keys in taken_periods must be tuples of type (integer, integer).")
                day, slot = key
                if day not in DAYS:
                    inv_days_str = ", ".join(f"'{a}'" for a in DAYS)
                    raise ValueError(f"Invalid day '{day}' in taken_periods keys. Each key must be one of: {inv_days_str}.")
                if not isinstance(slot, int) or 0 > slot:
                    raise ValueError(f"Slot must be a non-negative integer. Sent '{slot}'.")
                if not isinstance(value, list) or not all(isinstance(period, int) for period in value):
                    raise ValueError(f"taken_periods value for key '{key}' must be a list of integers. Sent {value}.")
        
        self.taken_periods = taken_periods

    @staticmethod
    def from_json(json_string : str) -> 'Availability':
        data = json.loads(json_string)
        invalid_keys = set(int(k) for k in data.keys()) - set(DAYS)
        if invalid_keys:
            inv_keys_str = ", ".join(f"'{a}'" for a in invalid_keys)
            inv_days_str = ", ".join(f"'{a}'" for a in DAYS)
            raise ValueError(f"Invalid keys in availability data: {inv_keys_str}. Each key must be one of: {inv_days_str}")
        filtered = {}
        for day in DAYS:
            slots = data.get(str(day), [])
            for slot in slots:
                if not isinstance(slot, int) or not (0 <= slot <= 23):
                    raise ValueError(f"Slots in Availaility must be non-negative integers. Sent '{slot}'.")
            filtered[day] = slots
        return Availability(filtered)
    
    def remove(self, day: int, slot: int, mask: list[int]) -> bool:
        from ..utils import check_occurrence_desc
        
        # Check if slot exists for the given day
        if slot not in self.slots[day]:
            return False
        
        # Check if the mask conflicts with already taken periods
        if not check_occurrence_desc(mask, self.taken_periods.get((day, slot), [])):
            return False
        
        # If no mask, remove the slot completely
        if not mask:
            self.slots[day].remove(slot)
            # Also remove from taken_periods if it exists
            if (day, slot) in self.taken_periods:
                del self.taken_periods[(day, slot)]
            return True
        
        # Add mask to taken periods for this (day, slot)
        if (day, slot) not in self.taken_periods:
            self.taken_periods[(day, slot)] = []
        self.taken_periods[(day, slot)].extend(mask)
        return True
