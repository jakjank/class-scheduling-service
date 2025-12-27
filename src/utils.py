from . import *
import copy
import random
from itertools import product

def covers(hours: list[int], start: int, duration: int) -> bool:
    # true if [start, start+duration) is in hours
    return all(h in hours for h in range(start, start + duration))

def check_period_mask(needed_periods: list[int], taken_periods: list[int]) -> bool:
    # only groups can have defined by user period mask 
    # (user passes needed ints for exampe 1 and 2 for even and odd weeks).
    # Teacher and Room may get taken for for example odd weeks while looking for solution.
    # therefor we need to check if group happening on odd weeks
    # does not get assinged to room already reserved for odd weeks
    if len(needed_periods) == 0 and len(taken_periods) != 0:
        return False
    for t in taken_periods:
        if t in needed_periods:
            return False
    return True

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
            triples.append((day, hour, duration))
            if not is_cluster_satisfied(copy.deepcopy(cluster.range), triples):
                return False
    return True

def get_all_placements_for_group(g : Group, prob : Problem):
    solutions = []
    days = list(g.availability.hours.keys())

    for day in days:
        av_hours = list(g.availability.hours[day])

        for start in av_hours:
            if not covers(av_hours, start, g.duration):
                continue
            
            for teacher_id in g.teacher_ids:
                teacher = prob.teachers[teacher_id]
                t_hours = teacher.availability.hours.get(day, [])
                if not covers(t_hours, start, g.duration) or not check_period_mask(g.period_mask, teacher.availability.taken_periods.get((day, start), [])):
                    break
            
                # find rooms
                # list of lists of rooms where all rooms in a list are fullfiling one set of labels
                # if we have labels [[a,b], [c]] 
                # then if the result is [[1,2,3],[7,10]]
                # [1,2,3] are satisfaing labels 'a' and 'b and [7,10] are satisfyig 'c'.
                # if no labels (labels = []) then the ok rooms is [[x]] where x is the list od all rooms
                # satisfying other parameters. 
                ok_rooms = []
                if not g.labels:
                    ok_rooms.append([])
                    for room in prob.rooms.values():
                        if not covers(room.availability.hours.get(day, []), start, g.duration):
                            continue

                        if room.capacity < g.capacity:
                            continue

                        if not check_period_mask(g.period_mask, room.availability.taken_periods.get((day, start), [])):
                            continue
                        
                        ok_rooms[0].append(room.id) 
                else:
                    for l in g.labels:
                        rooms_for_labels = []
                        for room in prob.rooms.values():
                            if not covers(room.availability.hours.get(day, []), start, g.duration):
                                continue
                            
                            # Check if all labels in l are present in room.labels
                            if not all(label in room.labels for label in l):
                                continue

                            if room.capacity < g.capacity:
                                continue

                            if not check_period_mask(g.period_mask, room.availability.taken_periods.get((day, start), [])):
                                continue

                            rooms_for_labels.append(room.id)
                        ok_rooms.append(rooms_for_labels)

                found_rooms = True
                for rooms in ok_rooms:
                    if not rooms:
                        found_rooms = False
                        break

                if found_rooms:
                    if check_clustering(g, day, start, g.duration, prob):
                        solutions.append((g.id, g.teacher_ids, ok_rooms, day, start, g.period_mask))

    return solutions

def get_random_record(placements : list) -> Record:
    # single placement in placements returned by get_all_placements_for_group()
    # has concrete time and a list of all availbale rooms
    # so we get random placement and then chose random rooms out of all available
    random_placement = random.choice(placements)
    
    group_id, teacher_ids, all_rooms, day, hour, period_mask = random_placement
    # all_rooms is a list of lists, one list per label set
    # we need to pick one room from each label set
    selected_rooms = [random.choice(room_list) for room_list in all_rooms]
    
    return Record(group_id, teacher_ids, selected_rooms, day, hour, period_mask)

def get_best_record(placements : list, prob : Problem, rating_function):
    # unwrap placements
    unwrapped = []

    for p in placements:
        group_id, teacher_ids, all_rooms, day, hour, period_mask = p
        for combo in product(*all_rooms):
            combo = list(combo)
            unwrapped.append(Record(group_id, teacher_ids, combo, day, hour, period_mask))

    unwrapped.sort(key=lambda r: rating_function(r, prob), reverse=True)
    return unwrapped[0]
        