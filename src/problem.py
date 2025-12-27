from . import Teacher, Room, Group, Course, Cluster, Record
import copy

def pad_number(num: int) -> str:
    return f"{num:03d}"

class Problem:
    def __init__(self, teachers=None, rooms=None, groups=None, courses=None, clusters=None, records=None):
        self.teachers = teachers if teachers is not None else {}
        self.rooms = rooms if rooms is not None else {}
        self.groups = groups if groups is not None else {}
        self.courses = courses if courses is not None else {}
        self.clusters = clusters if clusters is not None else []
        self.records = records if records is not None else  []

    def add_teacher(self, teacher: Teacher):
        self.teachers[teacher.id] = teacher

    def add_room(self, room: Room):
        self.rooms[room.id] = room

    def add_group(self, group: Group):
        self.groups[group.id] = group

    def add_course(self, course: Course):
        self.courses[course.id] = course
    
    def add_cluster(self, cluster: Cluster):
        self.clusters.append(cluster)

    def add_record(self, record: Record):
        self.records.append(record)

    def add_record_and_update_availability(self, record : Record) -> bool:
        day, start_hour, mask = record.day, record.hour, record.period_mask
        duration = self.groups[record.group_id].duration

        for t_id in record.teachers_ids:
            for h in range(start_hour, start_hour + duration):
                if not self.teachers[t_id].book_time_slot(day, h, mask):
                    return False
                
        for r_id in record.rooms_ids:
            for h in range(start_hour, start_hour + duration):
                if not self.rooms[r_id].book_time_slot(day, h, mask):
                    return False
                
        # I think it is not necessery to update group availability
        # as we want look at it anymore after adding an record
        self.records.append(record)
        return True
    
    def check(self, only_records=False):
        def check_constraints(record: Record, group: Group) :
            if(msg := self.check_group_availability(record, group)):
                return msg

            if (msg := self.check_teacher_availability(record, group)):
                return msg

            if (msg := self.check_teacher_conflicts(record, group)):
                return msg

            if (msg := self.check_room_availability(record, group)):
                return msg

            if (msg := self.check_room_conflicts(record, group)):
                return msg

            if (msg := self.check_room_labels(record, group)):
                return msg

            if (msg := self.check_room_capacity(record, group)):
                return msg

            if (msg := self.check_cluster_constraints(record, group)):
                return msg
        
        if(only_records):
            for record in self.records:
                group = self.groups.get(record.group_id, None)

                if group == None:
                    return f"record with group_id {record.group_id} exists, but ther is no group with such id"
                if (msg := check_constraints(record, group)):
                        return msg
        else:
            for group in self.groups.values():
                record = None
                for rec in self.records:
                    if rec.group_id == group.id:
                        record = rec
                if not record:
                    return f"{self.courses[group.course_id].name} group with id={group.id} is not present in solution"

                if (msg := check_constraints(record, group)):
                    return msg
            
        return "0"

    def check_teacher_availability(self, record: Record, group: Group):
        """Ensure all teachers are available at the scheduled time."""
        for teacher_id in record.teachers_ids:
            teacher = self.teachers[teacher_id]
            if record.hour not in teacher.availability.hours[record.day]:
                return f"Teacher {teacher.name} (id={teacher.id}) is not available on {record.day} between {record.hour} and {record.hour + group.duration}"

    def check_teacher_conflicts(self, record: Record, group: Group):
        """Ensure the teacher has no other class at the time"""
        for teacher_id in record.teachers_ids:
            for other in self.records:
                if other.group_id == record.group_id or other.day != record.day:
                    continue

                if teacher_id in other.teachers_ids:
                    if other.hour in range(record.hour, record.hour + group.duration):
                        if (len(list(set(self.groups[other.group_id].period_mask) & set(self.groups[group.id].period_mask))) > 0 or
                            not self.groups[other.group_id].period_mask or
                            not self.groups[group.id].period_mask):
                            start = min(other.hour, record.hour)
                            end = max(other.hour + self.groups[other.group_id].duration,
                                      record.hour + group.duration)
                            return f"Teacher {self.teachers[teacher_id].name} (id={teacher_id}) has conflicting classes on {record.day} between {start} and {end}"

    def check_room_availability(self, record: Record, group: Group):
        for room_id in record.rooms_ids:
            room_avail = self.rooms[room_id].availability.hours[record.day]
            for hour in range(record.hour, record.hour + group.duration):
                if hour not in room_avail:
                    return f"Room with id={room_id} is not available on {record.day} between {record.hour} and {record.hour + group.duration}"

    def check_room_conflicts(self, record: Record, group: Group):
        """Ensure no overlapping use of the same room."""
        rooms_ids = record.rooms_ids
        record_rooms = set(rooms_ids)

        for other in self.records:
            if other.group_id == record.group_id or other.day != record.day:
                continue

            # Shared room?
            shared_rooms = list(record_rooms & set(other.rooms_ids))
            if shared_rooms:
                # Overlapping time?
                if other.hour in range(record.hour, record.hour + group.duration):
                    if (len(set(self.groups[other.group_id].period_mask) & set(self.groups[group.id].period_mask)) > 0 or
                            not self.groups[other.group_id].period_mask or
                            not self.groups[group.id].period_mask):
                        room_ids_str = ", ".join(str(rid) for rid in shared_rooms)
                        return f"At least two groups (id={group.id}, id={other.group_id}) use room(s) with id={room_ids_str} in the same time on {record.day} between {record.hour} and {record.hour + group.duration}"

    def check_room_labels(self, record: Record, group: Group):
        """Ensure assigned rooms have required labels."""
        for labels in group.labels:
            if not any(set(labels).issubset(set(self.rooms[room_id].labels)) for room_id in record.rooms_ids):
                room_labels = [self.rooms[room_id].labels for room_id in record.rooms_ids]
                return f"{self.courses[group.course_id].name} group with id={group.id} has room(s) with labels={room_labels} but needs labels={group.labels}"

    def check_room_capacity(self, record: Record, group: Group):
        """Ensure assigned rooms have enough capacity."""
        for room_id in record.rooms_ids:
            if self.rooms[room_id].capacity < group.capacity:
                return f"{self.courses[group.course_id].name} group with id={group.id} has capacity={group.capacity} but has assigned room (id={room_id}) with capacity={self.rooms[room_id].capacity}"

    def check_cluster_constraints(self, record: Record, group: Group):
        """Ensure clusters meet day/hour range constraints."""
        def is_cluster_satisfied(cluster: list[int], triples: list[tuple]):
            # Sort in descending order to use larger blocks first
            cluster.sort(reverse=True)

            # Group triples by day
            days_triples = {}
            for triple in triples:
                day = triple[0]
                if day not in days_triples:
                    days_triples[day] = []
                days_triples[day].append(triple)
            
            # Process each day
            for day, day_triples in days_triples.items():
                # Sort by start hour
                day_triples.sort(key=lambda t: t[1])
                
                # Calculate the total span from earliest to latest
                earliest_h = min(t[1] for t in day_triples)
                latest_h = max(t[1] + t[2] for t in day_triples)
                span = latest_h - earliest_h
                
                # Try to find a cluster block that can cover this span
                found = False
                for i in range(len(cluster)):
                    if cluster[i] >= span:
                        del cluster[i]
                        found = True
                        break
                
                # If no single block can cover the span, try using multiple blocks
                if not found:
                    # Find continuous segments (no gaps)
                    segments = []
                    current_start = day_triples[0][1]
                    current_end = day_triples[0][1] + day_triples[0][2]
                    
                    for i in range(1, len(day_triples)):
                        triple_start = day_triples[i][1]
                        triple_end = day_triples[i][1] + day_triples[i][2]
                        
                        if triple_start > current_end:
                            # Gap found, save current segment
                            segments.append(current_end - current_start)
                            current_start = triple_start
                            current_end = triple_end
                        elif triple_start == current_end:
                            # Adjacent (touching), could merge or keep separate
                            # Keep separate to allow multiple blocks
                            segments.append(current_end - current_start)
                            current_start = triple_start
                            current_end = triple_end
                        else:
                            # Overlapping, must merge
                            current_end = max(current_end, triple_end)
                    
                    # Save the last segment
                    segments.append(current_end - current_start)
                    
                    # Try to match all segments with cluster blocks
                    segments.sort(reverse=True)
                    for segment_size in segments:
                        matched = False
                        for i in range(len(cluster)):
                            if cluster[i] >= segment_size:
                                del cluster[i]
                                matched = True
                                break
                        if not matched:
                            return False
                        
            return True

        def check_clustering(g: Group, day: str, hour: int, duration: int, prob: Problem) -> bool:
            clusters = prob.clusters
            for cluster in clusters:
                if g.id in cluster.groups_ids:
                    records = [r for r in prob.records if r.group_id in cluster.groups_ids]
                    triples = list(zip([r.day for r in records], 
                                    [r.hour for r in records], 
                                    [prob.groups[r.group_id].duration for r in records]))
                    if not is_cluster_satisfied(copy.deepcopy(cluster.range), triples):
                        return False
            return True

        for cluster in self.clusters:
            if group.id not in cluster.groups_ids:
                continue
            else:
                if not check_clustering(group, record.day, record.hour, group.duration, self):
                    group_ids_str = ", ".join(str(id) for id in sorted(cluster.groups_ids))
                    return f"Cluster connecting groups with ids {group_ids_str} is not satisfied"
        
                
    def check_group_availability(self, record: Record, group: Group):
        for hour in range(record.hour, record.hour + group.duration):
            if hour not in group.availability.hours[record.day]:
                return f"{self.courses[group.course_id].name} group with id={group.id} cannot take place on {record.day} between {record.hour} and {record.hour + group.duration}"