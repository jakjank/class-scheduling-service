from . import Allocation, Problem
import copy

ALGORITHMS_AVAILABLE = ["probabilistic_alg", "ordered_groups_alg", "rating_function_alg"]

class Response:
    def __init__(self, status: int, msg: str, solution: list[Allocation]):
        self.status = status
        self.msg = msg
        self.solution = solution

    def __repr__(self) -> str:
        sorted_solution = sorted(self.solution, key=lambda r: r.group_id)
        solution_str = "\n".join(f"  {allocation}," for allocation in sorted_solution)

        return (
            f"Response(status={self.status}, msg='{self.msg}', solution=[\n"
            f"{solution_str}\n" 
            f"])"
        )

class Solver:
    problem : Problem

    def __init__(self):
        self.problem = None

    def solve(self, problem : Problem, method : str) -> Response:
        from .algorithms import random_solve, ordered_groups_solve, rating_function_solve

        precheck = problem.check(only_allocations=True)
        if precheck != "0":
            precheck = "Given assignments do not satisfy constraints: " + precheck
            return Response(1, precheck, [])
        
        self.problem = problem
        response = None
        match method:
            case "probabilistic_alg": response = random_solve(copy.deepcopy(problem))
            case "ordered_groups_alg": response = ordered_groups_solve(copy.deepcopy(problem))
            case "rating_function_alg": response = rating_function_solve(copy.deepcopy(problem))
            case _: response = Response(1, f"Not a valid method! ({method})", [])

        if response.status != 0:
            return response
        
        for r in problem.allocations:
            if r not in response.solution:
                raise RuntimeError(f"Solver has a bug! User established allocations were affected while looking for a solution with method={method}. Please raise an issue.")
        
        problem.allocations = response.solution

        if problem.check() != "0":
            raise RuntimeError(f"Solver has a bug! Solving with method={method} created solution which does not pass Problem.check. Please raise an issue.")
        
        return response
