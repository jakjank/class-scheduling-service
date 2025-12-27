import copy
import random
from . import *
from .utils import get_all_placements_for_group, get_random_record, get_best_record

class Response:
    def __init__(self, status: int, msg: str, solution: list[Record]):
        self.status = status
        self.msg = msg
        if self.status == 0:
            self.solution = solution
        else:
            self.solution = []

def rating_function(record : Record, prob : Problem):
        grade = 0

        # free seats in room
        for room_id in record.rooms_ids:
            free_seats = prob.rooms[room_id].capacity - prob.groups[record.group_id].capacity 
            if free_seats <= 10:
                grade += 2
            if 10 < free_seats < 20:
                grade +=1

        # days off for teacher
        for teacher_id in record.teachers_ids:
            has_already_classes_on_this_day = False
            for r in prob.records:
                if teacher_id in r.teachers_ids:
                    if r.day == record.day:
                        has_already_classes_on_this_day = True
                        break

            if has_already_classes_on_this_day:
                grade += 2

        # free mon and fri (only if teacher has no classes already on mon or fri)
        for teacher_id in record.teachers_ids:
            has_already_classes_on_mon = False
            has_already_classes_on_fri = False
            for r in prob.records:
                if teacher_id in r.teachers_ids:
                    if r.day == "mon":
                        has_already_classes_on_mon = True
                    if r.day == "fri":
                        has_already_classes_on_fri = True

            if not has_already_classes_on_mon and record.day != "mon":
                grade += 2
            if not has_already_classes_on_fri and record.day != "fri":
                grade += 2

        # even starting hour
        if record.hour % 2 == 0:
            grade += 5

        # not too early and not too late
        if 10 <= record.hour <= 17:
            grade += 2

        # TODO studnets votes

        return grade

class Solver:
    problem : Problem

    def __init__(self):
        self.problem = None

    def solve(self, problem : Problem, option : int) -> Response:
        precheck = problem.check(only_records=True)
        if precheck != "0":
            precheck = "Given assignments do not satisfy constraints: " + precheck
            return Response(1, precheck, [])
        
        self.problem = problem
        solution = None
        match option:
            case 0: solution = self.random_solve(copy.deepcopy(problem))
            case 1: solution = self.random_ordered_groups_solve(copy.deepcopy(problem))
            case 2: solution = self.with_rating_function_solve(copy.deepcopy(problem))
            case _: solution = self.random_solve(copy.deepcopy(problem))

        if solution.status != 0:
            return solution
        
        for r in problem.records:
            if r not in solution.solution:
                return Response(1, f"Solver has a bug! Established records were afected while looking for solution with option={option}. Contact PLG.", [])
        
        problem.records = solution.solution

        if problem.check() != "0":
            return Response(1, f"Solver has a bug! Solving with option={option} created solution which does not pass Problem.check. Contact PLG.", [])
        
        return solution

    def random_solve(self, prob: Problem) -> Response:

        established_groups = [r.group_id for r in prob.records]
        groups     = list(prob.groups.values())
        teachers   = list(prob.teachers.values())
        rooms      = list(prob.rooms.values())

        # remove established groups from groups
        groups = [g for g in groups if g.id not in established_groups]

        # delete established records and re-add to delete availabilities
        copy_records = copy.deepcopy(prob.records)
        prob.records = []
        for r in copy_records:
            prob.add_record_and_update_availability(r)

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
                return Response(1, "Could not find placement for group " + str(g.id) + "RANDOM_SOLVE", [])
            
            # add random placement to soulution and delete availabilities
            random_record = get_random_record(placements) 
            if not prob.add_record_and_update_availability(random_record):
                return Response(1, "Unexpected error while looking for solution", [])

        return Response(0, "Success", prob.records)
    
    def random_ordered_groups_solve(self, prob: Problem):

        def number_of_possible_placements(g : Group):
            placements = get_all_placements_for_group(g,prob)
            count = 0
            for p in placements:
                # because assigment is specific hour and all possible rooms
                count += min(len(lst) for lst in p[2])
            return count

        established_groups = [r.group_id for r in prob.records]
        groups     = list(prob.groups.values())

        # sort groups bu difficulty
        # find number of possible placements for each group
        map_group_id_difficulty = {}
        for g in groups:
            map_group_id_difficulty[g.id] = number_of_possible_placements(g)

        # to all groups in each cluster assign highest difficulty from this cluster
        # (may not work as expected when one group is in multiple clusters)
        for c in prob.clusters:
            max_difficulty_in_cluster = min(map_group_id_difficulty[g_id] for g_id in c.groups_ids)
            for g_id in c.groups_ids:
                map_group_id_difficulty[g_id] = max_difficulty_in_cluster

        groups.sort(key=lambda g: map_group_id_difficulty[g.id])

        # remove established groups from groups
        groups = [g for g in groups if g.id not in established_groups]

        # delete established records and re-add to delete availabilities
        copy_records = copy.deepcopy(prob.records)
        prob.records = []
        for r in copy_records:
            prob.add_record_and_update_availability(r)

        while len(groups) > 0:
            # get next group
            g = groups.pop(0)

            # get all possible terms and rooms for a group
            placements = get_all_placements_for_group(g, prob)

            if len(placements) == 0:
                # not very useful msg
                return Response(1, "Could not find placement for group " + str(g.id) + "ORDERED_SOLVE", [])
            
            # add random placement to soulution and delete availabilities
            random_record = get_random_record(placements) 
            if not prob.add_record_and_update_availability(random_record):
                return Response(1, "Unexpected error while looking for solution", [])

        return Response(0, "Success", prob.records)
    
    def with_rating_function_solve(self, prob: Problem):
        def number_of_possible_placements(g : Group):
            placements = get_all_placements_for_group(g,prob)
            count = 0
            for p in placements:
                # because assigment is specific hour and all possible rooms
                count += min(len(lst) for lst in p[2])
            return count

        established_groups = [r.group_id for r in prob.records]
        groups     = list(prob.groups.values())

        # remove established groups from groups
        groups = [g for g in groups if g.id not in established_groups]

        # delete established records and re-add to delete availabilities
        copy_records = copy.deepcopy(prob.records)
        prob.records = []
        for r in copy_records:
            prob.add_record_and_update_availability(r)

        # sort groups ascending by number of placements in empty timetable
        groups.sort(key=lambda g: number_of_possible_placements(g))

        # maybe move clustered groups to the front

        while len(groups) > 0:
            # get next group
            g = groups.pop(0)

            # get all possible terms and rooms for a group
            placements = get_all_placements_for_group(g, prob)

            if len(placements) == 0:
                # not very useful msg
                return Response(1, "Could not find placement for group " + str(g.id) + "RATING_SOLVE", [])
            
            # chose best placement according to rating function
            best_placement = get_best_record(placements, prob, rating_function)

            # add placement to soulution and delete availabilities
            if not prob.add_record_and_update_availability(best_placement):
                return Response(1, "Unexpected error while looking for solution", [])

        return Response(0, "Success", prob.records)