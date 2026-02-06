from .utils import get_all_placements_for_group
from src import Problem
from src.communication import Response, Issue
import random
import copy

def random_solve(prob: Problem) -> Response:

    established_groups = [r.group_id for r in prob.allocations]
    groups     = list(prob.groups.values())
    teachers   = list(prob.teachers.values())
    rooms      = list(prob.rooms.values())

    # remove established groups from groups
    groups = [g for g in groups if g.id not in established_groups]

    # delete established allocations and re-add to delete availabilities
    copy_allocations = copy.deepcopy(prob.allocations)
    prob.allocations = []
    for r in copy_allocations:
        prob.add_allocation_and_update_availability(r)

    random.shuffle(groups)
    random.shuffle(teachers)
    random.shuffle(rooms)

    while len(groups) > 0:
        # get next group
        g = groups.pop(0)

        # get all possible terms and rooms for a group
        placements = get_all_placements_for_group(g, prob)

        if len(placements) == 0:
            # not very useful msg
            return Response(False, [Issue("group", g.id, f"Could not find placement for group with id={g.id} (RANODM_SOLVE)")], prob.allocations)
        
        # add random placement to soulution and delete availabilities
        random_allocation = random.choice(placements)
        if not prob.add_allocation_and_update_availability(random_allocation):
            return Response(False, [Issue("other", 0, "Unexpected error while looking for solution")], [])

    return Response(True, [], prob.allocations)
