from fastapi import FastAPI, Request
import uvicorn
from src import Parser, Solver, Response
from src import Request as req

# Create the FastAPI app
app = FastAPI()
parser = Parser()
solver = Solver()

@app.post("/solve")
async def solve_problem(request: Request):
    problem_json_string = await request.body()
    result = solve_main(problem_json_string.decode('utf-8'))
    return result

def solve_main(problem_json_string: str):
    try:
        request = parser.parse(problem_json_string)
        result  = solver.solve(request.problem, request.option)
        return result
    except Exception as e:
        return Response(1, f"Error: {str(e)}", [])
 
if __name__ == "__main__":
    # Start uvicorn server on port 7999, listening on all interfaces
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=False)

