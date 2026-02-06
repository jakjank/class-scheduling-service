from src.problem import Problem
from src.algorithms import random_solve, ordered_groups_solve, rating_function_solve, deep_ordered_groups_solve
from src.communication import Response, Issue
import copy

ALGORITHMS_AVAILABLE = {
    "probabilistic_alg": random_solve,
    "ordered_groups_alg": ordered_groups_solve,
    "rating_function_alg": rating_function_solve,
    "deep_ordered_groups_alg": deep_ordered_groups_solve
}

class Solver:
    problem : Problem

    def __init__(self):
        self.problem = None

    def solve(self, problem : Problem, method : str) -> Response:
        failed_constraints = problem.precheck()
        if failed_constraints:
            precheck = f"Failed precheck. Given assignments do not satisfy constraints."
            failed_constraints.append(Issue("other", 0, precheck))
            return Response(False, failed_constraints, [])
        
        self.problem = problem
        if method not in ALGORITHMS_AVAILABLE:
            raise ValueError(f"Not a valid method! ({method})")
        
        response = ALGORITHMS_AVAILABLE[method](copy.deepcopy(problem))

        if not response.success:
            return response
        
        for r in problem.allocations:
            if r not in response.solution:
                raise RuntimeError(f"Solver has a bug! User established allocations were affected while looking for a solution with method={method}. Please raise an issue.")
        
        problem.allocations = response.solution

        if problem.check() != []:
            raise RuntimeError(f"Solver has a bug! Solving with method={method} created solution which does not pass Problem.check. Please raise an issue.")
        
        return response
