from . import Problem, Group, Allocation
from itertools import product, permutations
from collections import deque
import random
import copy

def covers(slots: list[int], start: int, duration: int) -> bool:
    # true if [start, start+duration) is in slots
    return all(h in slots for h in range(start, start + duration))

def check_occurrence_desc(needed_periods: list[int], taken_periods: list[int]) -> bool:
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

def is_cluster_satisfied(cluster: list[int], day_slot_duration: list[tuple]):

    def do_not_overlap(day_slot_duration: list[tuple]):
        slots = [[s for s in range(triple[0]*1000 + triple[1], triple[0]*1000 + triple[1] + triple[2])] for triple in day_slot_duration]
        s = set()
        for list in slots:
            for el in list:
                if el in s:
                    return False
                s.add(el)
        return True


    def get_slots_used(day_slot_duration: list[tuple]) -> list[int]:
        slots_set = set()
        for triple in day_slot_duration:
            # TODO: be smarter, remember smh max slot id, for all in request
            # Probably wont be more than 1000 slots per day but its only an assumption
            slot_of_week = (triple[0] - 1) * 1000 + triple[1]
            duration = triple[2]
            for slot in range(slot_of_week, slot_of_week + duration):
                slots_set.add(slot)
        slots_list = list(slots_set)
        slots_list.sort()
        return slots_list
    
    def delete_slots_covered_by_blocks(slots: deque[int], blocks: list[int]) -> list[int]:
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
            return delete_slots_covered_by_blocks(slots, blocks[1:])

    if cluster == []:
        return do_not_overlap(day_slot_duration)

    slots_used = get_slots_used(day_slot_duration)

    if len(slots_used) > sum(cluster):
        return False

    for perm in permutations(cluster):
        slots = deque(slots_used)
        if not delete_slots_covered_by_blocks(slots, perm):
            return True
    return False

def check_clustering(g: Group, day: str, slot: int, duration: int, prob: Problem) -> bool:
    clusters = prob.clusters
    for cluster in clusters:
        if g.id in cluster.groups_ids:
            allocations = [r for r in prob.allocations if r.group_id in cluster.groups_ids]
            triples = list(zip([r.day for r in allocations], 
                            [r.slot for r in allocations], 
                            [prob.groups[r.group_id].duration for r in allocations]))
            triples.append((day, slot, duration))
            if not is_cluster_satisfied(copy.deepcopy(cluster.range), triples):
                return False
    return True

def get_all_placements_for_group(g : Group, prob : Problem):
    solutions = []
    days = list(g.availability.slots.keys())

    for day in days:
        av_slots = list(g.availability.slots[day])

        for start in av_slots:
            if not covers(av_slots, start, g.duration):
                continue
            time_suits_teachers = True
            if g.teacher_ids:
                for teacher_id in g.teacher_ids:
                    teacher = prob.teachers[teacher_id]
                    t_slots = teacher.availability.slots.get(day, [])
                    if not covers(t_slots, start, g.duration) or not check_occurrence_desc(g.occurrence_desc, teacher.availability.taken_periods.get((day, start), [])):
                        time_suits_teachers = False
                        break

            if not time_suits_teachers:
                continue

            # find rooms
            # list of lists of rooms where all rooms in a list are fullfiling one set of labels
            # if we have labels [[a,b], [c]]
            # then if the result is [[1,2,3,7],[7,10]]
            # [1,2,3,7] are satisfaing labels 'a' and 'b and [7,10] are satisfyig 'c'.
            # if no labels (labels = []) then we mark rooms_needed=False
            rooms_needed  = True
            ok_rooms = []
            if not g.labels: # group does not need any room
                rooms_needed = False
            else:
                for labels_DNF in g.labels:
                    rooms_for_labels = []
                    for room in prob.rooms.values():
                        if room.id in rooms_for_labels:
                            #do not add same room twice
                            continue

                        if not covers(room.availability.slots.get(day, []), start, g.duration):
                            continue
                        
                        # Check if all labels in l are present in room.labels
                        if not room.satisfies_labels_DNF(labels_DNF):
                            continue

                        if room.capacity < g.capacity:
                            continue

                        if not check_occurrence_desc(g.occurrence_desc, room.availability.taken_periods.get((day, start), [])):
                            continue

                        rooms_for_labels.append(room.id)
                    ok_rooms.append(rooms_for_labels)

            found_rooms = True
            if rooms_needed:
                for rooms in ok_rooms:
                    if not rooms:
                        found_rooms = False
                        break

            if found_rooms:
                if check_clustering(g, day, start, g.duration, prob):
                    solutions.append((g.id, ok_rooms, day, start))

    return solutions

def get_random_allocation(placements : list) -> Allocation:
    # single placement in placements returned by get_all_placements_for_group()
    # has concrete time and a list of all availbale rooms
    # so we get random placement and then chose random rooms out of all available
    random_placement = random.choice(placements)
    
    group_id,all_rooms, day, slot= random_placement
    # all_rooms is a list of lists, one list per label set
    # we need to pick one room from each label set
    selected_rooms = [random.choice(room_list) for room_list in all_rooms]
    
    return Allocation(group_id,selected_rooms, day, slot)

def get_best_allocation(placements : list, prob : Problem, rating_function):
    # unwrap placements
    unwrapped = []

    for p in placements:
        group_id, all_rooms, day, slot = p
        for combo in product(*all_rooms):
            combo = list(combo)
            unwrapped.append(Allocation(group_id, combo, day, slot))

    scored = [(r, rating_function(r, prob)) for r in unwrapped]
    best_score = max(score for _, score in scored)
    best_assignments = [r for r, score in scored if (score == best_score or score >= best_score-2)]
    return random.choice(best_assignments)


def number_of_possible_placements(g : Group, prob : Problem):
    placements = get_all_placements_for_group(g, prob)
    count = 0
    for placement in placements:
        # because assigment is specific slot and all possible rooms
        # TODO some groups dont have rooms at all
        rooms = placement[1]
        if rooms:
            count += min(len(list_of_rooms) for list_of_rooms in rooms)
        else:
            # heuristic: if group does not need any rooms,
            # it is easier to assign than group which can use any of the available rooms
            count += len(prob.rooms) + 1
    return count
