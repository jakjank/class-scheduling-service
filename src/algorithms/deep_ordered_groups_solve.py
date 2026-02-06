from .utils import get_all_placements_for_group, number_of_possible_placements
from src import Problem
from src.communication import Response, Issue
from src.models import Group
import random
import copy

def order_groups(prob: Problem, remaining_groups: list[Group]) -> list[Group]:
    map_group_id_difficulty = {}
    for g in remaining_groups:
        map_group_id_difficulty[g.id] = number_of_possible_placements(g, prob)
    
    for c in prob.clusters:
        max_difficulty_in_cluster = min(map_group_id_difficulty[g_id] if g_id in map_group_id_difficulty else 86400 for g_id in c.group_ids)
        for g_id in c.group_ids:
            map_group_id_difficulty[g_id] = max_difficulty_in_cluster

    remaining_groups.sort(key=lambda g: map_group_id_difficulty[g.id])

    return remaining_groups


def deep_ordered_groups_solve(prob: Problem) -> Response:
    established_groups = [r.group_id for r in prob.allocations]
    groups     = list(prob.groups.values())

    # remove established groups from groups
    groups = [g for g in groups if g.id not in established_groups]

    groups = order_groups(prob, groups)

    # delete user established allocations and re-add to delete availabilities
    copy_allocations = copy.deepcopy(prob.allocations)
    prob.allocations = []
    for alloc in copy_allocations:
        prob.add_allocation_and_update_availability(alloc)

    while len(groups) > 0:
        # get next group
        g = groups.pop(0)

        # get all possible terms and rooms for a group
        placements = get_all_placements_for_group(g, prob)

        if len(placements) == 0:
            # not very useful msg
            return Response(False, [Issue("group", g.id, f"Could not find placement for group with id={g.id} (DEEP_ORDERED_SOLVE)")], prob.allocations)
        
        # add random placement to soulution and delete availabilities
        random_allocation = random.choice(placements) 
        if not prob.add_allocation_and_update_availability(random_allocation):
            return Response(False, [Issue("other", 0, "Unexpected error while looking for solution")], [])
        
        groups = order_groups(prob, groups)

    return Response(True, [], prob.allocations)
