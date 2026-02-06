# Project Architecture

## Main Script

`main.py` is the main entry point of the application. It defines the FastAPI server, exposes HTTP endpoints, and coordinates request parsing, validation, and problem solving using the `Parser` and the `Solver`.

## Parser

Parses the requests from JSON to internal objects. While doing so it checks for logical or semantic errors in the request.

## Solver

Serves as an interface to the *algorithms*. First it ensures user defined allocations are do not break any constraints. Then it passes the problem to further to the chosen algorithm. Lastly it ensures that the algorithm produced valid group allocations and returns the solution.

## Schedule request flow

```mermaid
sequenceDiagram
    User->>main.py: Request
    main.py->>parser.py: Parse
    Note over parser.py: parse and validate
    parser.py->>main.py: Parsed Request
    main.py->>solver.py: problem & alg. name
    Note over solver.py: do precheck
    solver.py->>algorithm:
    Note over algorithm: Schedule groups
    algorithm->>solver.py:
    Note over solver.py: do postcheck
    solver.py->>main.py: solution
    main.py->>User: Response
```

## Check request flow

```mermaid
sequenceDiagram
    User->>main.py: Request
    main.py->>parser.py: Parse
    Note over parser.py: parse and validate
    parser.py->>main.py: Parsed Request
    main.py->>Problem: check()
    Note over Problem: check if groups are assigned correctly
    Problem->>main.py: Message
    main.py->>User: Response
```