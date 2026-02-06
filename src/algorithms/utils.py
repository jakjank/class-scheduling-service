from src.models import Group, Allocation, Availability
from src import Problem
from itertools import product
import random

def covers(slots: list[int], start: int, duration: int) -> bool:
    # true if [start, start+duration) is in slots
    return all(h in slots for h in range(start, start + duration))

def get_all_placements_for_group(g: Group, prob: Problem) -> list[Allocation]:

    def unwrap(placements: list) -> list[Allocation]:
        unwrapped = []
        for p in placements:
            group_id, all_rooms, day, slot = p
            for combo in product(*all_rooms):
                combo = list(combo)
                unwrapped.append(Allocation(group_id, combo, day, slot))
        return unwrapped

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
                    if not covers(t_slots, start, g.duration) or not Availability.check_occurrence_desc(g.occurrence_desc, teacher.availability.taken_periods.get((day, start), [])):
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

                        if not Availability.check_occurrence_desc(g.occurrence_desc, room.availability.taken_periods.get((day, start), [])):
                            continue

                        rooms_for_labels.append(room.id)
                    ok_rooms.append(rooms_for_labels)

            found_rooms = True
            if rooms_needed:
                for rooms in ok_rooms:
                    if not rooms:
                        found_rooms = False
                        break

            clusters_satisfied = True
            if found_rooms:
                for c in prob.clusters:
                    if g.id in c.group_ids:
                        if not c.can_use_slots(day, list(range(start, start+g.duration))):
                            clusters_satisfied = False
                            break

            if clusters_satisfied and found_rooms:
                solutions.append((g.id, ok_rooms, day, list(range(start, start+g.duration))))

    return unwrap(solutions)

def get_best_allocation(allocations: list[Allocation], prob: Problem, rating_function) -> Allocation:
    scored = [(r, rating_function(r, prob)) for r in allocations]
    best_score = max(score for _, score in scored)
    best_assignments = [r for r, score in scored if (score == best_score or score >= best_score-2)]
    return random.choice(best_assignments)


def number_of_possible_placements(g: Group, prob: Problem) -> int:
    return len(get_all_placements_for_group(g, prob))
