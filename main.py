from fastapi import FastAPI
import uvicorn
from src import Parser, Solver
from src.communication import Response, Issue
import json

app = FastAPI()
parser = Parser()
solver = Solver()

@app.post("/schedule")
async def schedule_endpoint(request: dict):
    result = main(json.dumps(request), False)
    return result

@app.post("/check")
async def check_endpoint(request: dict):
    result = main(json.dumps(request), True)
    return result
 
def main(problem_json_string: str, just_check: bool) -> Response:
    try:
        if just_check:
            request = parser.parse(problem_json_string, check_request=True)
            check_msg = request.problem.check(method=request.method)
            if check_msg == []:
                return Response(True, [], [])
            else:
                return Response(False, check_msg, [])
        else:
            request = parser.parse(problem_json_string)
            return solver.solve(request.problem, request.method)
    except RuntimeError as e:
        return Response(False, [Issue("runtime_error", 0, e.args[0])], [])
    except KeyError as e:
        return Response(False, [Issue("key_error", 0, e.args[0])], [])
    except ValueError as e:
        return Response(False, [Issue("value_error", 0, e.args[0])], [])
    except Exception as e:
        return Response(False, [Issue("other", 0, f"Unknown Error happend: '{e.args[0]}'. Please raise an issue")], [])

if __name__ == "__main__":
    # Start uvicorn server on port 7999
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=False)
