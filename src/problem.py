from . import Teacher, Room, Group, Cluster, Allocation

class Problem:
    def __init__(
        self,
        teachers=None,
        rooms=None,
        groups=None,
        clusters=None,
        allocations=None
    ):
        self.teachers = teachers if teachers is not None else {}
        self.rooms    = rooms    if rooms    is not None else {}
        self.groups   = groups   if groups   is not None else {}
        self.clusters = clusters if clusters is not None else []
        self.allocations = allocations if allocations  is not None else []

    def add_teacher(self, teacher: Teacher):
        if teacher.id in self.teachers:
            raise ValueError(f"Teachers should have unique ids. Id '{teacher.id}' repeats.")
        self.teachers[teacher.id] = teacher

    def add_room(self, room: Room):
        if room.id in self.rooms:
            raise ValueError(f"Rooms should have unique ids. Id '{room.id}' repeats.")
        self.rooms[room.id] = room

    def add_group(self, group: Group):
        if group.id in self.groups:
            raise ValueError(f"Groups should have unique ids. Id '{group.id}' repeats.")
        self.groups[group.id] = group
    
    def add_cluster(self, cluster: Cluster):
        self.clusters.append(cluster)

    def add_allocation(self, allocation: Allocation):
        # TODO: check if group exists?
        self.allocations.append(allocation)

    def add_allocation_and_update_availability(self, allocation : Allocation) -> bool:
        day, start_slot, mask = allocation.day, allocation.slot, self.groups[allocation.group_id].occurrence_desc
        duration = self.groups[allocation.group_id].duration

        for t_id in self.groups[allocation.group_id].teacher_ids:
            for h in range(start_slot, start_slot + duration):
                if not self.teachers[t_id].book_time_slot(day, h, mask):
                    return False
                
        for r_id in allocation.room_ids:
            for h in range(start_slot, start_slot + duration):
                if not self.rooms[r_id].book_time_slot(day, h, mask):
                    return False
                
        # I think it is not necessery to update group availability
        # as we want look at it anymore after adding an allocation
        self.allocations.append(allocation)
        return True
    
    def check(self, only_allocations=False):
        def check_constraints(allocation: Allocation, group: Group) :
            if(msg := self.check_group_availability(allocation, group)):
                return msg

            if (msg := self.check_teacher_availability(allocation, group)):
                return msg

            if (msg := self.check_teacher_conflicts(allocation, group)):
                return msg

            if (msg := self.check_room_availability(allocation, group)):
                return msg

            if (msg := self.check_room_conflicts(allocation, group)):
                return msg

            if (msg := self.check_room_labels(allocation, group)):
                return msg

            if (msg := self.check_room_capacity(allocation, group)):
                return msg

            if (msg := self.check_cluster_constraints(allocation, group)):
                return msg
        
        if(only_allocations):
            for allocation in self.allocations:
                group = self.groups.get(allocation.group_id, None)

                if group == None:
                    return f"allocation with group_id {allocation.group_id} exists, but ther is no group with such id"
                if (msg := check_constraints(allocation, group)):
                        return msg
        else:
            for group in self.groups.values():
                allocation = None
                for rec in self.allocations:
                    if rec.group_id == group.id:
                        allocation = rec
                if not allocation:
                    return f"Group with id={group.id} is not present in solution"

                if (msg := check_constraints(allocation, group)):
                    return msg
            
        return "0"

    def check_teacher_availability(self, allocation: Allocation, group: Group):
        """Ensure all teachers are available at the scheduled time."""
        for teacher_id in group.teacher_ids:
            teacher = self.teachers[teacher_id]
            if allocation.slot not in teacher.availability.slots[allocation.day]:
                return f"Teacher with id={teacher.id} is not available on {allocation.day} between {allocation.slot} and {allocation.slot + group.duration}"

    def check_teacher_conflicts(self, allocation: Allocation, group: Group):
        """Ensure the teacher has no other class at the time"""
        for teacher_id in group.teacher_ids:
            for other in self.allocations:
                if other.group_id == allocation.group_id or other.day != allocation.day:
                    continue

                if teacher_id in self.groups[other.group_id].teacher_ids:
                    if other.slot in range(allocation.slot, allocation.slot + group.duration):
                        if (len(list(set(self.groups[other.group_id].occurrence_desc) & set(self.groups[group.id].occurrence_desc))) > 0 or
                            not self.groups[other.group_id].occurrence_desc or
                            not self.groups[group.id].occurrence_desc):
                            start = min(other.slot, allocation.slot)
                            end = max(other.slot + self.groups[other.group_id].duration,
                                      allocation.slot + group.duration)
                            return f"Teacher with id={teacher_id} has conflicting classes on {allocation.day} between {start} and {end}"

    def check_room_availability(self, allocation: Allocation, group: Group):
        for room_id in allocation.room_ids:
            room_avail = self.rooms[room_id].availability.slots[allocation.day]
            for slot in range(allocation.slot, allocation.slot + group.duration):
                if slot not in room_avail:
                    return f"Room with id={room_id} is not available on {allocation.day} between {allocation.slot} and {allocation.slot + group.duration}"

    def check_room_conflicts(self, allocation: Allocation, group: Group):
        """Ensure no overlapping use of the same room."""
        room_ids = allocation.room_ids
        allocation_rooms = set(room_ids)

        for other in self.allocations:
            if other.group_id == allocation.group_id or other.day != allocation.day:
                continue

            # Shared room?
            shared_rooms = list(allocation_rooms & set(other.room_ids))
            if shared_rooms:
                # Overlapping time?
                if other.slot in range(allocation.slot, allocation.slot + group.duration):
                    if (len(set(self.groups[other.group_id].occurrence_desc) & set(self.groups[group.id].occurrence_desc)) > 0 or
                            not self.groups[other.group_id].occurrence_desc or
                            not self.groups[group.id].occurrence_desc):
                        room_ids_str = ", ".join(str(rid) for rid in shared_rooms)
                        return f"At least two groups (id={group.id}, id={other.group_id}) use room(s) with id={room_ids_str} in the same time on {allocation.day} between {allocation.slot} and {allocation.slot + group.duration}"

    def check_room_labels(self, allocation: Allocation, group: Group):
        """Ensure assigned rooms have required labels."""
        for labels_DNF in group.labels:
            if not any(self.rooms[r_id].satisfies_labels_DNF(labels_DNF) for r_id in allocation.room_ids):
                room_labels = [self.rooms[r_id].labels for r_id in allocation.room_ids]
                return f"Group with id={group.id} has room(s) with labels={room_labels} but needs labels={group.labels}"

    def check_room_capacity(self, allocation: Allocation, group: Group):
        """Ensure assigned rooms have enough capacity."""
        for room_id in allocation.room_ids:
            if self.rooms[room_id].capacity < group.capacity:
                return f"Group with id={group.id} has capacity={group.capacity} but has assigned room (id={room_id}) with capacity={self.rooms[room_id].capacity}"

    def check_cluster_constraints(self, allocation: Allocation, group: Group):
        """Ensure clusters meet day/slot range constraints."""
        from .utils import check_clustering

        for cluster in self.clusters:
            if group.id not in cluster.groups_ids:
                continue
            else:
                if not check_clustering(group, allocation.day, allocation.slot, group.duration, self):
                    group_ids_str = ", ".join(str(id) for id in sorted(cluster.groups_ids))
                    return f"Cluster connecting groups with ids {group_ids_str} is not satisfied"
        
                
    def check_group_availability(self, allocation: Allocation, group: Group):
        for slot in range(allocation.slot, allocation.slot + group.duration):
            if slot not in group.availability.slots[allocation.day]:
                return f"Group with id={group.id} cannot take place on {allocation.day} between {allocation.slot} and {allocation.slot + group.duration}"
            
    def __str__(self):
        return (
            'Problem<'
            f"groups = {len(self.groups)}, "
            f"teachers = {len(self.teachers)}, "
            f"rooms = {len(self.rooms)}, "
            f"clusters = {len(self.clusters)}, "
            f"allocations = {len(self.allocations)}>" 
        )
