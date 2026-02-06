import json
from itertools import permutations
from collections import deque
from src.models import Allocation

class Cluster:
    def __init__(self, id: int, range: list[int], group_ids: list[int]):
        if not isinstance(id, int):
            raise ValueError(f"Field 'id' value in cluster must be an integer. Sent '{id}'.")
        self.id = id
        if not all(isinstance(el, int) for el in range):
            raise ValueError(f"Field 'range' value in cluster must be a list of integers. Sent '{range}'.")
        self.range = range
        self.group_ids = group_ids
        self.allocations = []

    @staticmethod
    def from_json(json_string : str) -> 'Cluster':
        REQUIRED_FIELDS = ['id', 'range', 'group_ids']
        data = json.loads(json_string)
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            missing_str = ", ".join(f"'{a}'" for a in missing)
            raise KeyError(f"Cluster is missing required fields: {missing_str}")
        
        id = data.get('id')
        range = data.get('range')
        group_ids = data.get('group_ids')
        return Cluster(id, range, group_ids)
    
    def add_allocation(self, alloc: Allocation) -> None:
        if (alloc.group_id in self.group_ids and
            alloc not in self.allocations):
            self.allocations.append(alloc)

    def do_not_overlap(self, extra_day=None, extra_slots=None) -> bool:
        slots_used_per_alloc = [[slot + alloc.day*86400 for slot in alloc.slots] for alloc in self.allocations]
        if extra_day:
            slots_used_per_alloc.append([extra_day*86400 + s for s in extra_slots])
        s = set()
        for l in slots_used_per_alloc:
            for el in l:
                if el in s:
                    return False
                s.add(el)
        return True
    
    def get_slots_ascending(self, extra_day=None, extra_slots=None) -> list[int]:
        slots_set = set()
        slots = [
            slot + alloc.day * 86400
            for alloc in self.allocations
            for slot in alloc.slots
        ]
        if extra_day:
            for s in extra_slots:
                slots.append(extra_day*86400 + s)
        for slot in slots:
            slots_set.add(slot)
        slots_list = list(slots_set)
        slots_list.sort()
        return slots_list

    def try_to_delete_slots_with_blocks(self, slots: deque[int], blocks: list[int]) -> list[int]:
        # slots must be sorted ascending and with no repetitions
        if not slots or not blocks:
            return slots
        else:
            earliest_slot = slots[0]
            for h in range(earliest_slot, earliest_slot+blocks[0]):
                if slots:
                    if slots[0] == h:
                        slots.popleft()
                else:
                    return slots
            return self.try_to_delete_slots_with_blocks(slots, blocks[1:])

    def check(self) -> bool:
        if self.range == []:
            return self.do_not_overlap()
        
        for perm in permutations(self.range):
            slots = deque(self.get_slots_ascending())
            if not self.try_to_delete_slots_with_blocks(slots, perm):
                return True
        return False
    
    def can_use_slots(self, day: int, slots: list[int]) -> bool:
        if self.range == []:
            return self.do_not_overlap(day, slots)
        
        for perm in permutations(self.range):
            slots = deque(self.get_slots_ascending(day, slots))
            if not self.try_to_delete_slots_with_blocks(slots, perm):
                return True
        return False
