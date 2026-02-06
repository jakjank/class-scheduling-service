from src.models import Allocation

ISSUE_TYPES = [
    "runtime_error",
    "value_error",
    "key_error",
    "allocation",
    "availability",
    "cluster",
    "group",
    "room",
    "teacher",
    "parser",
    "problem",
    "solver",
    "other"
]

class Issue:
    def __init__(self, type: str, id: int, msg: str):
        if type not in ISSUE_TYPES:
            type = "other"
        self.type = type
        self.id = id
        self.msg = msg

# msg can be both string and a list of strings
class Response:
    def __init__(self, success: bool, issues: list[Issue], solution: list[Allocation]):
        self.success = success
        self.errors = []
        for issue in issues:
            self.errors.append(
                {
                    "type": issue.type,
                    "id": issue.id,
                    "msg:" : issue.msg
                }
            )
        self.solution = solution

    def __repr__(self) -> str:
        sorted_solution = sorted(self.solution, key=lambda r: r.group_id)
        solution_str = "\n".join(f"  {allocation}," for allocation in sorted_solution)

        return (
            f"Response(success={self.success},\n"
            f"errors=[\n"
            f"{self.errors}"
            f"],"
            f"solution=[\n"
            f"{solution_str}\n" 
            f"])"
        )
