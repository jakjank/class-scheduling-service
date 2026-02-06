from src.models import Room, Group, Teacher, Cluster, Allocation
from src import Problem, CHECK_OPTIONS, ALGORITHMS_AVAILABLE
from src.communication import Query
import json

class Parser:
    def parse(self, json_data: str, check_request=False) -> Query:
        problem = Problem()
        data = json.loads(json_data)

        method = data.get("method", None)
        if check_request:
            if method not in CHECK_OPTIONS and method:
                check_opt_str = ", ".join(f"'{a}'" for a in CHECK_OPTIONS)
                raise ValueError(f"field 'method' value in Request to '/check' endpoint must be one of the following: {check_opt_str}. Sent '{method}'.")
        else:
            if method not in ALGORITHMS_AVAILABLE and method:
                alg_opt_str = ", ".join(f"'{a}'" for a in ALGORITHMS_AVAILABLE)
                raise ValueError(f"field 'method' value in Request to '/schedule' endpoint must be one of the following: {alg_opt_str}. Sent '{method}'.")
        
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

        return Query(problem, method)
