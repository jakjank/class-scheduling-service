from .utils import get_all_placements_for_group, number_of_possible_placements, get_best_allocation
from src import Problem
from src.communication import Response, Issue
from src.models import Allocation
from typing import Callable
import copy

def rating_function(allocation : Allocation, prob : Problem) -> int:
        grade = 0

        # free seats in room
        for room_id in allocation.room_ids:
            free_seats = prob.rooms[room_id].capacity - prob.groups[allocation.group_id].capacity 
            if free_seats <= 10:
                grade += 2
            if 10 < free_seats < 20:
                grade +=1

        # days off for teacher
        for teacher_id in prob.groups[allocation.group_id].teacher_ids:
            has_already_classes_on_this_day = False
            for alloc in prob.allocations:
                if teacher_id in prob.groups[allocation.group_id].teacher_ids:
                    if alloc.day == allocation.day:
                        has_already_classes_on_this_day = True
                        break

            if has_already_classes_on_this_day:
                grade += 2

        # free 1 and 5 (only if teacher has no classes already on 1 or 5)
        for teacher_id in prob.groups[allocation.group_id].teacher_ids:
            has_already_classes_on_mon = False
            has_already_classes_on_fri = False
            for alloc in prob.allocations:
                if teacher_id in prob.groups[allocation.group_id].teacher_ids:
                    if alloc.day == 1:
                        has_already_classes_on_mon = True
                    if alloc.day == 5:
                        has_already_classes_on_fri = True

            if not has_already_classes_on_mon and allocation.day != 1:
                grade += 2
            if not has_already_classes_on_fri and allocation.day != 5:
                grade += 2

        # even starting slot
        if min(allocation.slots) % 2 == 0:
            grade += 5

        # not too early and not too late
        if 10 <= min(allocation.slots) <= 17:
            grade += 2

        # TODO student votes

        return grade

def rating_function_solve(prob: Problem, rating_function : Callable[[Allocation, Problem], int]=rating_function) -> Response:

    established_groups = [r.group_id for r in prob.allocations]
    groups     = list(prob.groups.values())

    # remove established groups from groups
    groups = [g for g in groups if g.id not in established_groups]

    # delete established allocations and re-add to delete availabilities
    copy_allocations = copy.deepcopy(prob.allocations)
    prob.allocations = []
    for alloc in copy_allocations:
        prob.add_allocation_and_update_availability(alloc)

    # sort groups ascending by number of placements in empty timetable
    groups.sort(key=lambda g: number_of_possible_placements(g, prob))

    # maybe move clustered groups to the front

    while len(groups) > 0:
        # get next group
        g = groups.pop(0)

        # get all possible terms and rooms for a group
        placements = get_all_placements_for_group(g, prob)

        if len(placements) == 0:
            # not very useful msg
            return Response(False, [Issue("group", g.id, f"Could not find placement for group with id={g.id} (RATING_SOLVE)")], prob.allocations)
        
        # chose best placement according to rating function
        best_placement = get_best_allocation(placements, prob, rating_function)

        # add placement to soulution and delete availabilities
        if not prob.add_allocation_and_update_availability(best_placement):
            return Response(False, [Issue("other", 0, "Unexpected error while looking for solution")], [])

    return Response(True, [], prob.allocations)
