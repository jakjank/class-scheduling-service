from dataclasses import dataclass, field
from typing import Dict, List
import json

class Availability:
    hours: Dict[str, List[int]] = field(default_factory=lambda: {day: [] for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']})
    taken_periods: Dict = field(default_factory=dict)

    def __init__(self, dir : dict, taken_periods = None):
        valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        invalid_keys = set(dir.keys()) - set(valid_days)
        if invalid_keys:
            raise ValueError(f"Invalid keys in availability data: {invalid_keys}")
        filtered = {}
        for day in valid_days:
            hours = dir.get(day, [])
            for hour in hours:
                if not isinstance(hour, int) or not (0 <= hour <= 23):
                    raise ValueError(f"Invalid hour '{hour}' for day '{day}'. Hours must be integers in 0-23 range.")
            filtered[day] = hours
        self.hours = filtered
        
        # Future-proofing since user can set taken_periods in availiility for any class now.
        # User can only set period_mask in groups 
        # Validate taken_periods format: keys should be (day, hour) tuples, values should be lists of integers
        if taken_periods is None:
            taken_periods = {}
        
        if taken_periods:
            for key, value in taken_periods.items():
                if not isinstance(key, tuple) or len(key) != 2:
                    raise ValueError(f"Invalid taken_periods key '{key}'. Keys must be tuples of (day, hour).")
                day, hour = key
                if day not in valid_days:
                    raise ValueError(f"Invalid day '{day}' in taken_periods key. Must be one of {valid_days}.")
                if not isinstance(hour, int) or not (0 <= hour <= 23):
                    raise ValueError(f"Invalid hour '{hour}' in taken_periods key. Must be integer in 0-23 range.")
                if not isinstance(value, list):
                    raise ValueError(f"Invalid taken_periods value for key {key}. Values must be lists of integers.")
                for period in value:
                    if not isinstance(period, int):
                        raise ValueError(f"Invalid period '{period}' in taken_periods[{key}]. All periods must be integers.")
        
        self.taken_periods = taken_periods

    @staticmethod
    def from_json(json_string : str) -> 'Availability':
        data = json.loads(json_string)
        valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        invalid_keys = set(data.keys()) - set(valid_days)
        if invalid_keys:
            raise ValueError(f"Invalid keys in availability data: {invalid_keys}")
        filtered = {}
        for day in valid_days:
            hours = data.get(day, [])
            for hour in hours:
                if not isinstance(hour, int) or not (0 <= hour <= 23):
                    raise ValueError(f"Invalid hour '{hour}' for day '{day}'. Hours must be integers in 0-23 range.")
            filtered[day] = hours
        return Availability(filtered)
    
    def remove(self, day: str, hour: int, mask: list[int]) -> bool:
        # Import here to avoid circular dependency
        from ..utils import check_period_mask
        
        # Check if hour exists for the given day
        if hour not in self.hours[day]:
            return False
        
        # Check if the mask conflicts with already taken periods
        if not check_period_mask(mask, self.taken_periods.get((day, hour), [])):
            return False
        
        # If no mask, remove the hour completely
        if not mask:
            self.hours[day].remove(hour)
            # Also remove from taken_periods if it exists
            if (day, hour) in self.taken_periods:
                del self.taken_periods[(day, hour)]
            return True
        
        # Add mask to taken periods for this (day, hour)
        if (day, hour) not in self.taken_periods:
            self.taken_periods[(day, hour)] = []
        self.taken_periods[(day, hour)].extend(mask)
        return True
        