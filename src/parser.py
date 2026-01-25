from . import Room, Group, Teacher, Cluster, Allocation
from .problem import Problem
import json

class Request:
    def __init__(self, problem: Problem, method: str):
        self.problem = problem
        self.method = method

class Parser:
    def parse(self, json_data: str) -> Request:
        from .solver import ALGORITHMS_AVAILABLE
        
        problem = Problem()
        data = json.loads(json_data)

        method = data.get("method", "probabilistic_alg")
        if method not in ALGORITHMS_AVAILABLE and method:
            alg_avail_str = ", ".join(f"'{a}'" for a in ALGORITHMS_AVAILABLE)
            raise ValueError(f"field 'method' values in Request must be one of the following: {alg_avail_str}. Sent '{method}'.")
        
        for room in data.get('rooms', []):
            problem.add_room(Room.from_json(json.dumps(room)))
        for group in data.get('groups', []):
            problem.add_group(Group.from_json(json.dumps(group)))
        for teacher in data.get('teachers', []):
            problem.add_teacher(Teacher.from_json(json.dumps(teacher)))
        for cluster in data.get('clusters', []):
            problem.add_cluster(Cluster.from_json(json.dumps(cluster)))
        
        established = data.get("allocations", [])
        for allocation in established:
            problem.add_allocation(Allocation.from_json(json.dumps(allocation)))

        return Request(problem, method)
