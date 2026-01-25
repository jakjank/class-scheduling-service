from src import get_all_placements_for_group, get_random_allocation, number_of_possible_placements
from src import Problem, Response
import copy

def ordered_groups_solve(prob: Problem):
    established_groups = [r.group_id for r in prob.allocations]
    groups     = list(prob.groups.values())

    # sort groups bu difficulty
    # find number of possible placements for each group
    map_group_id_difficulty = {}
    for g in groups:
        map_group_id_difficulty[g.id] = number_of_possible_placements(g, prob)

    # to all groups in each cluster assign highest difficulty from this cluster
    # (may not work as expected when one group is in multiple clusters)
    for c in prob.clusters:
        max_difficulty_in_cluster = min(map_group_id_difficulty[g_id] for g_id in c.groups_ids)
        for g_id in c.groups_ids:
            map_group_id_difficulty[g_id] = max_difficulty_in_cluster

    groups.sort(key=lambda g: map_group_id_difficulty[g.id])

    # remove established groups from groups
    groups = [g for g in groups if g.id not in established_groups]

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
            return Response(1, "Could not find placement for group with id=" + str(g.id) + ". (ORDERED_SOLVE)", prob.allocations)
        
        # add random placement to soulution and delete availabilities
        random_allocation = get_random_allocation(placements) 
        if not prob.add_allocation_and_update_availability(random_allocation):
            return Response(1, "Unexpected error while looking for solution", [])

    return Response(0, "Success", prob.allocations)
