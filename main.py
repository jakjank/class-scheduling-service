from fastapi import FastAPI, Request
import uvicorn
from src import Parser, Solver, Response

app = FastAPI()
parser = Parser()
solver = Solver()

@app.post("/schedule")
async def schedule_endpoint(request: Request):
    problem_json_string = await request.body()
    result = main(problem_json_string.decode('utf-8'), False)
    return result

@app.post("/check")
async def check_endpoint(request: Request):
    problem_json_string = await request.body()
    result = main(problem_json_string.decode('utf-8'), True)
    return result
 
def main(problem_json_string: str, only_check):
    try:
        request = parser.parse(problem_json_string)
        if only_check:
            check_msg = request.problem.check()
            if check_msg == "0":
                return Response(0, "", request.problem.allocations)
            else:
                return Response(1, check_msg, [])
        return solver.solve(request.problem, request.method)
    except RuntimeError as e:
        return Response(1, f"{str(e)}", [])
    except KeyError as e:
        return Response(1, f"{str(e)}", [])
    except ValueError as e:
        return Response(1, f"{str(e)}", [])
    except Exception as e:
        return Response(1, f"Unknown Error happend: '{str(e)}'. Please raise an issue", [])

if __name__ == "__main__":
    # Start uvicorn server on port 7999
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=False)
