from . import Teacher, Room, Group, Cluster, Allocation
from src.communication import Issue

CHECK_OPTIONS = ["full_check", "simple_check"]

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

    def add_teacher(self, teacher: Teacher) -> None:
        if teacher.id in self.teachers:
            raise ValueError(f"Teachers should have unique ids. Id '{teacher.id}' repeats.")
        self.teachers[teacher.id] = teacher

    def add_room(self, room: Room) -> None:
        if room.id in self.rooms:
            raise ValueError(f"Rooms should have unique ids. Id '{room.id}' repeats.")
        self.rooms[room.id] = room

    def add_group(self, group: Group) -> None:
        if group.id in self.groups:
            raise ValueError(f"Groups should have unique ids. Id '{group.id}' repeats.")
        self.groups[group.id] = group
    
    def add_cluster(self, cluster: Cluster) -> None:
        exisiting_cluster_ids = [c.id for c in self.clusters]
        if cluster.id in exisiting_cluster_ids:
            raise ValueError(f"Clusters should have unique ids. Id '{cluster.id}' repeats.")
        self.clusters.append(cluster)
        for alloc in self.allocations:
            if alloc.group_id in cluster.group_ids:
                cluster.add_allocation(alloc)

    def add_allocation(self, allocation: Allocation) -> None:
        # TODO: check if group exists?
        self.allocations.append(allocation)
        for cluster in self.clusters:
            if allocation.group_id in cluster.group_ids:
                cluster.add_allocation(allocation)

    def add_allocation_and_update_availability(self, allocation : Allocation) -> bool:
        day, slots, mask = allocation.day, allocation.slots, self.groups[allocation.group_id].occurrence_desc

        for t_id in self.groups[allocation.group_id].teacher_ids:
            for h in slots:
                if not self.teachers[t_id].book_time_slot(day, h, mask):
                    return False
                
        for r_id in allocation.room_ids:
            for h in slots:
                if not self.rooms[r_id].book_time_slot(day, h, mask):
                    return False
        
        for c in self.clusters:
            c.add_allocation(allocation)
            if not c.check():
                return False
                
        # I think it is not necessery to update group availability
        # as we want look at it anymore after adding an allocation
        self.allocations.append(allocation)
        return True
    
    def check_constraints(self, allocation: Allocation, group: Group, full_check: bool) -> list[Issue]:
            fails = []
            if not group:
                issue = Issue("allocation", allocation.group_id, f"allocation with group_id {allocation.group_id} exists, but ther is no group with such id.")
                return [issue]

            checks_to_do = [
                self.check_group_availability,
                self.check_teacher_availability,
                self.check_teacher_conflicts,
                self.check_room_availability,
                self.check_room_conflicts,
                self.check_room_labels,
                self.check_room_capacity,
                self.check_cluster_constraints,
                self.check_cluster_slots
            ]
            for fun in checks_to_do:
                issues = fun(allocation, group)
                if issues:
                    if full_check:
                        fails.extend(issues)
                    else:
                        return issues
                
            return fails

    def check(self, method="simple_check") -> list[Issue]:        
        full_check = method == "full_check"
        failed_constraints = []
        
        for group in self.groups.values():

            allocation = None
            for rec in self.allocations:
                if rec.group_id == group.id:
                    allocation = rec

            if not allocation:
                issue = Issue("group", group.id, f"Group with id={group.id} is not present in solution")
                if full_check:
                    failed_constraints.append(issue)
                else:
                    return [issue]
            
            issues = self.check_constraints(allocation, group, full_check)
            if issues:
                if full_check:
                        failed_constraints.extend(issues)
                else:
                    return issues
            
        return failed_constraints
    
    def precheck(self) -> list[Issue]:
        failed_constraints = []
        for allocation in self.allocations:
            group = self.groups.get(allocation.group_id, None)
            issues = self.check_constraints(allocation, group, True)
            if issues:
                failed_constraints.extend(issues)
        return failed_constraints

    def check_teacher_availability(self, allocation: Allocation, group: Group) -> list[Issue]:
        """Ensure all teachers are available at the scheduled time."""
        issues = []
        for teacher_id in group.teacher_ids:
            teacher = self.teachers[teacher_id]
            if not all(s in teacher.availability.slots[allocation.day] for s in allocation.slots):
                issues.append(Issue("teacher", teacher_id, f"Teacher with id={teacher.id} is not available on {allocation.day} in each slot out of {allocation.slots}"))
        return issues

    def check_teacher_conflicts(self, allocation: Allocation, group: Group) -> list[Issue]:
        """Ensure the teacher has no other class at the time"""
        issues = []
        for teacher_id in group.teacher_ids:
            for other in self.allocations:
                if other.group_id == allocation.group_id or other.day != allocation.day:
                    continue

                if teacher_id in self.groups[other.group_id].teacher_ids:
                    if any(other_s in allocation.slots for other_s in other.slots):
                        if (len(list(set(self.groups[other.group_id].occurrence_desc) & set(self.groups[group.id].occurrence_desc))) > 0 or
                            not self.groups[other.group_id].occurrence_desc or
                            not self.groups[group.id].occurrence_desc):
                            issues.append(Issue("teacher", teacher_id, f"Teacher with id={teacher_id} has conflicting classes on {allocation.day}"))
        return issues

    def check_room_availability(self, allocation: Allocation, group: Group) -> list[Issue]:
        issues = []
        for room_id in allocation.room_ids:
            room_avail = self.rooms[room_id].availability.slots[allocation.day]
            for slot in allocation.slots:
                if slot not in room_avail:
                    issues.append(Issue("room", room_id, f"Room with id={room_id} is not available on {allocation.day} in slots {allocation.slots}"))
        return issues

    def check_room_conflicts(self, allocation: Allocation, group: Group) -> list[Issue]:
        """Ensure no overlapping use of the same room."""
        issues = []
        room_ids = allocation.room_ids
        allocation_rooms = set(room_ids)

        for other in self.allocations:
            if other.group_id == allocation.group_id or other.day != allocation.day:
                continue

            # Shared room?
            shared_rooms = list(allocation_rooms & set(other.room_ids))
            for room_id in shared_rooms:
                # Overlapping time?
                if any(other_s in allocation.slots for other_s in other.slots):
                    if (len(set(self.groups[other.group_id].occurrence_desc) & set(self.groups[group.id].occurrence_desc)) > 0 or
                            not self.groups[other.group_id].occurrence_desc or
                            not self.groups[group.id].occurrence_desc):
                        issues.append(Issue("room", room_id, f"At least two groups (id={group.id}, id={other.group_id}) use room with id={room_id} at the same time on {allocation.day} in slots {allocation.slots}"))
        return issues

    def check_room_labels(self, allocation: Allocation, group: Group) -> list[Issue]:
        """Ensure assigned rooms have required labels."""
        issues = []
        for labels_DNF in group.labels:
            if not any(self.rooms[r_id].satisfies_labels_DNF(labels_DNF) for r_id in allocation.room_ids):
                room_labels = [self.rooms[r_id].labels for r_id in allocation.room_ids]
                issues.append(Issue("group", group.id, f"Group with id={group.id} has room(s) with labels={room_labels} but needs labels={group.labels}"))
        return issues

    def check_room_capacity(self, allocation: Allocation, group: Group) -> list[Issue]:
        """Ensure assigned rooms have enough capacity."""
        issues = []
        for room_id in allocation.room_ids:
            if self.rooms[room_id].capacity < group.capacity:
                issues.append(Issue("room", room_id, f"Group with id={group.id} has capacity={group.capacity} but has assigned room (id={room_id}) with capacity={self.rooms[room_id].capacity}"))
        return issues

    def check_cluster_constraints(self, allocation: Allocation, group: Group) -> list[Issue]:
        """Ensure clusters meet day/slot range constraints."""
        issues = []
        for cluster in self.clusters:
            if group.id in cluster.group_ids:
                if not cluster.check():
                    group_ids_str = ", ".join(str(id) for id in sorted(cluster.group_ids))
                    issues.append(Issue("cluster", cluster.id, f"Cluster connecting groups with ids {group_ids_str} is not satisfied"))
        return issues
                
    def check_group_availability(self, allocation: Allocation, group: Group) -> list[Issue]:
        for slot in allocation.slots:
            if slot not in group.availability.slots[allocation.day]:
                return [Issue("allocation", group.id, f"Group with id={group.id} cannot take place on {allocation.day} in slots {allocation.slots}")]
    
    def check_cluster_slots(self, allocation: Allocation, group: Group) -> list[Issue]:
        first = min(allocation.slots)
        dur = group.duration
        if set(allocation.slots) - set(range(first, first + dur)):
            return [Issue("allocation", group.id, f"Allocation slots must be next natural numbers and their amoun must agree with group duration. Got {allocation.slots}.")]

    def __str__(self) -> str:
        return (
            'Problem<'
            f"groups = {len(self.groups)}, "
            f"teachers = {len(self.teachers)}, "
            f"rooms = {len(self.rooms)}, "
            f"clusters = {len(self.clusters)}, "
            f"allocations = {len(self.allocations)}>" 
        )
