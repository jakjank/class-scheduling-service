**Table of Contents**
* [A short introduction to scheduler](#short-introduction-to-scheduler)
  * [Starting the servie](#starting-the-service)
    * [Requirements](#requirements)
    * [Running the Service](#running-the-service)
    * [Running tests](#running-the-tests) todo
  * [Interacting with scheduler](#interacting-with-scheduler)
    * [Request schema](#message-schema)
      * [Request fields](#message-fields)
    * [Correctness of timetable](correctness-of-timetable)
    * [Response schema](#response-schema)
    * [Usage example](#usage-example)

# Short introduction to scheduler

Scheduler is a backend service for creating and validating timetables for educational institutions while respecting a variety of constraints, such as:
* Teacher availability
* Room types and capacities
* Relative start times of classes
* And several other scheduling rules
The service is designed primarily as a backend for timetable editors with a user-friendly UI, but it can also be used as a standalone application.

## Starting the service

The project is written in Python and built with FastAPI and Uvicorn.
You can run it either:
* Directly with Python, or
* Inside a Docker container (recommended)

### Requirements

* **Python** 3.11.14
* **FastAPI** 0.128.0
* **Uvicorn** 0.40.0
You may install all dependencies manually, but using Docker is strongly recommended for a simpler and more reproducible setup.
To build the Docker image, navigate to the root directory of the project and run:
```bash
$ docker build -t scheduler
```

### Running the Service

**Without Docker**
1. Make sure FastAPI and Uvicorn are installed.
2. Run the application:
```bash
python3 main.py
```
This will start the Uvicorn server at `http://0.0.0.0:7999`.

**With Docker**
Run the container with:
```bash
$ docker run -p 7999:7999 scheduler
```
The -p option maps port **7999** from the container to port **7999** on your machine, allowing you to interact with the service locally.

### Running Tests

Run all tests:
```bash
python3 -m unittest discover .
```

Run specific test:
```bash
python3 -m unittest tests.test_problem.TestProblem.test_check_teacher_conflicts
```

## Interacting with scheduler

The scheduler offer two HTTP endpoint to which you can post your requests:

`/schedule` - Accepts a scheduling problem and returns a JSON response with the solution or error information.

`POST /check` - Accepts a scheduling problem and returns a JSON response with confirmation or deny of correctness of sent assigments

### Request schema

The requests sent to both endpoint have very similar form. The only diference is that you should not define `method` field when sending reqest to `/check` endpoint. 

The request should be a JSON object with the following structure:

```json
{
  "method":      "algorithm_name",
  "teachers":    [...],
  "rooms":       [...],
  "groups":      [...],
  "clusters":    [...],
  "allocations": [...]
}
```

#### Request fields

The value of each field of the request, except `method`, is a list of objects which indirectly define constraints which must be met by the solution.
Below we explain what should a value of each field in the request be.

**Method**
The value of this field (string) indicates which algorithm should be used by the service to find the assigments for groups. Proper values are:
* `"probabilistic_alg"`,
* `"ordered_groups_alg"`, 
* and `"rating_function_alg"`

If value other then listed above is passed then the service will return message informing about this. To learn more about algorithms checkout [algorithms section](#algorithms)

**Teachers**
This field is a list of *Teacher* objects. The role of **Teacher** object is to represent real human availability.
**Teacher** object consists of following fields:
* id - the lecturer's unique identifier
* availability - a dictionary representing the slots per day in which the teacher is available. Days are keys and are in ISO-8601 format (1 is monday, 7 is sunday). The values in the dictionary are lists of natural numbers representing time slots. The mapping of individual slots to real rime slots is not imposed by the system and can be freely interpreted by the user. One may consider slot 0 to mean 7:30-8:15 time slot, 1 to mean 8:25-9:10 and so on and other may consider 8 to mean 8:00-9:00, 9 to mean 9:00-10:00 etc. In below and each next of the examples we will use the second interpretation. The numbers indicating slots must be non-negative and it is user's responsibility to use the same interpretation consistently across the whole request.

For example, the object below represents a teacher with $id = 66$ available on Mondays, Tuesdays, and Wednesdays from 8am to 4pm.

```json
{
    "id": 66,
    "availability": {
        "1": [8,9,10,11,12,13,14,15],
        "2": [8,9,10,11,12,13,14,15],
        "3": [8,9,10,11,12,13,14,15]
    }
}
```

**Rooms**
This field is a list of *Room* objects. Each **Room** object represents physical unit/room which are occupied by groups on certain times. **Room** object has following atributes:
* id - unique room identifier
* capacity - number of available seats
* availability - dictionary representing the dates when classes can be held, in the same format as the one described in Teacher
* labels - list of tags (strings) satisfied by the room

For example, the room defined below can accommodate 24 students. It is available Monday through Friday, 8:00 a.m. to 4:00 p.m., and has the tags *lab* and *linux*.
```json
{
    "id" : 11,
    "capacity" : 24,
        "availability" : {
            "1": [8,9,10,11,12,13,14,15],
            "2": [8,9,10,11,12,13,14,15],
            "3": [8,9,10,11,12,13,14,15],
            "4": [8,9,10,11,12,13,14,15],
            "5": [8,9,10,11,12,13,14,15],
            },
        "labels" : ["lab", "linux"]
}
```

**Groups**
List of **Group** objects. **Group** object defines activity group. The job of a service is to find an assigment (time and room(s)) for each group sent in **groups** field of request. The **Group** consist of following fields:
* id - a unique group identifier.
* duration - a natural number representing the duration on group in slots
* capacity - the maximum number of students who can enroll in the group
* availability - a dictionary representing the dates whan group can take place. Same format as the on in Teacher
* labels - a list of elements defining the labels that the group requires for its rooms. The number of elements in the list corresponds to the number of rooms required by the group. In particular, if the group uses a virtual room (there is no need to assign any physical rooms), the value of this field should be an empty list: "[]". Each element consists of a lists of tags describing group requirement for room as a DNF formula (refer to the example below). The labels field is optional and has a default value of "[]" (no rooms required)
* teacher_ids - a list of teacher IDs assigned to the group. This field is optional with a default value of "[]".
* occurrence_desc - a list of natural numbers specifying the cyclical nature of classes in subsequent periods (e.g., weeks). This field is optional with a default value of "[]".
An empty list means that classes are held every period (e.g., weekly).
If the occurrence_desc field contains at least one value, the group is held only during the periods designated by these values. The meaning of individual numbers is not imposed by the system and can be freely interpreted by the user (e.g., week number, week parity, week in which the Geminid meteor shower peaks, etc.).
The system considers the occurrence_desc field when detecting resource collisions (teachers and classrooms). Groups with non-empty occurrence_desc lists do not conflict with each other as long as the intersection of their occurrence_desc lists is empty. At the same time, groups with non-empty occurrence_desc lists conflict with groups realized in every period (i.e., with an empty occurrence_desc list).

The following object represents a group with $id = 70$, belonging to a course with $id = 7$. It lasts 2 slots and can accommodate 30 students. It can only meet on Mondays between 10:00 AM and 4:00 PM (according to used interpretation) and requires two rooms, one with the tags *TV* and *white_board* or with *projector* and the second toom with the tag *lab*. Teachers with IDs 66 and 3 teach this group. Remembering that the meaning of individual values ​​in the occurrence_desc field is not imposed by the system and can be freely interpreted by the user, in this example 2 could mean, for example, that classes are held on even weeks.

```json
{
    "id": 70,
    "course_id": 7,
    "duration": 2,
    "capacity": 30,
    "availability": {
        "1": [10, 11, 12, 13, 14, 15]
    },
    "labels": [[["TV", "white_board"], ["projector"]], [["lab"]]],
    "teacher_ids": [66, 3],
    "occurrence_desc": [2]
}
```

**Clusters**
List of **Cluster** objects. A **Cluster** is an object that defines time relationship between group assigments. It enables the user to require some groups to take time in the same time blocks or not to overlap at all. **Cluster** consists of the following fields:

* groups_id - a list of group IDs whose assignments must satisfy the cluster
* range - the number and length (in slots) of blocks in which groups must take place. Blocks do not have to appear in timetable in the order in which they are stored in *range* and can take place on the same or different days. If the range is an empty list then the groups realization times cannot overlap

The following example means that groups with IDs 11, 12, 13, and 14 must be held in two time blocks. The first block is two slots long, and the second one is four slots long.

```json
{
"groups_ids": [11, 12, 13, 14],
"range": [2, 4]
}
```

**Allocations**
This field is a list of **Allocation** objects. **Allocation** object defines an assigment of a group to the time and place. The response on succesfull request consists of such allocations. The user may send self established assigments in **allocations** field of a request. In such situation the service will first check if these assigments are correct and if so, it will try to create a plan with these allocations. Allocation object consist of the following fields:
* group_id - a unique group identifier for which assigment is made
* room_ids - a list of room IDs where the given class is to be held
* day - the day the given class is to be held (in format consisent with ISO-8601)
* slot - the number of slot the given class is to begin

For example, the allocation object below means that the group with $id=1$ with assigned room with $id$ 32 starts on Fridays at 10.
```json
{
    "group_id": 1,
    "room_ids": [32],
    "day": 5,
    "slot": 10
}
```

### Correctness of timetable
Before we check how the response looks like, lets informaly define what a correct timetable is.
The set of group assigments to time slots and room(s) is correct if all of the below points are met:
* Each group has rooms assigned so that the group's requirements for room tags are met
* The capacity of each room in which a given group's classes are held is sufficient to accommodate the entire group
* Each group meets at times (starting slots and all subsequent times based on the class duration) consistent with the group's availability
* Each group meets at times consistent with the availability of each assigned lecturer
* Each group meets at times consistent with the availability of each assigned room
* No lecturer teaches more than one group at a time. •No room is occupied by more than one group at a time
* All groups within a cluster meet in the blocks described by that cluster.


### Format of sent objects

Structure of each object sent in request to service (with example) is explained below.
All the fields in are requierd unless otherwise stated.

### Response Format

After sending a query to the solver, it returns a response in JSON format. It consists of three fields:
* status - A number indicating the success (0) or failure (1) of the query. In the case of a query to generate a solution (the query was sent to `/schedule` endpoint), failure means that the schedule could not be generated. In the case of a query to verify the solution (the query was sent to `/check` endpoint), failure means that the group assignments submitted in the *allocations* field do not satisfy the specified constraints.
* msg - A message sent by the solver. It may indicate a logical or semantic error in the submitted data or describe a problem encountered while generating or checking the schedule.
* solution - A list of allocations in the same format as the query. If *status* = 0 for the query to generate a schedule, this list contains the assignments of all groups; if *status* = 1, this list is empty. If the query was about the correctness of the solution and the sent allocations satisfied the constraints, then the returned value in the *solution* field has the same allocations as the *allocations* field in the query, otherwise the value of the *solution* field is "[]".

#### Success Response example
```json
{
    "status":0,
    "msg":"Success",
    "solution":[
        {
            "group_id":1,
            "rooms_ids":[32],
            "day":1,
            "slot":8
        },
        {
            "group_id":2,
            "room_ids":[32],
            "day":1,
            "slot":10
        }
    ]
}
```

#### Fail Response example
TODO: update?
```json
{
    "status":1,
    "msg":"Cluster connecting groups with ids 1, 2 is not satisfied",
    "solution":[]
}
```

### Usage Example
TODO

## Core Logic Classes

### main.py
Starts the service (uvicorn + FastAPI). Listens on endpoint, passes data to Parser and next to Solver. Lastly send response.

### Parser
- **Method**: `parse(json_data: str) -> Request`
- Converts JSON input into Python Problem objects
- Validates and deserializes all constraint objects
- Returns a `Request` object containing problem and algorithm choice

### Problem
- **Responsibilities**:
  - Store all constraints (teachers, rooms, groups, courses, clusters, allocations)
  - Track established (hardcoded) assignments
  - Provide constraint checking methods

- **Key Methods**:
  - `add_teacher()`, `add_room()`, `add_group()`, etc. - Add entities
  - `check(only_allocations=false)` - When `only_allocations=false` validates complete solution against all constraints. Otherwise only check if exisitng allocations do not break any constraints
  - `check_teacher_availability()` - Verify teacher availability
  - `check_room_availability()` - Verify room availability
  - `check_cluster_constraints()` - Verify cluster requirements
  - And more constraint simple validation methods used `check()`

### Solver
- **Responsibilities**:
  - Find valid timetable solutions using various algorithms
  - Return `Response` object with status and solution

- **Methods**:
  - `solve(problem, method)` - Only function. Starts with precheck to check user assigned allocations. Dispatches to algorithm chosen with `method` argument. Lastly check if produced solution is valid and return `Response` object.

### Utility Functions
- `covers(slots, start, duration)` - Check if time range is covered
- `check_occurrence_desc(needed, taken)` - Validate week constraints
- `is_cluster_satisfied(cluster, triples)` - Verify cluster satisfaction
- `check_clustering(group, day, slot, duration, problem)` - Validate new assignment against clusters
- `get_all_placements_for_group(group, problem)` - Find valid placements for a group

## Algorithms

### Random Solve
- Randomly shuffles groups, teachers, and rooms
- For each unscheduled group, finds all valid placements
- Randomly selects one valid placement
- Repeats until all groups are scheduled or no valid placement exists

## Project Structure

```
scheduling_service/
├── src/
│   ├── __init__.py           # Module exports
│   ├── parser.py             # JSON parser
│   ├── problem.py            # Problem definition and constraints
│   ├── solver.py             # Solver algorithms
│   ├── utils.py              # Utility functions
│   └── models/           # Data models
│       ├── availability.py
│       ├── cluster.py
│       ├── course.py
│       ├── group.py
│       ├── allocation.py
│       ├── room.py
│       ├── teacher.py
│       └── sync_cluster.py
├── tests/
│   ├── test_parser.py        # Parser tests
│   ├── test_problem.py       # Problem validation tests
│   ├── test_solver.py        # Solver algorithm tests
│   ├── test_utils.py         # Utility function tests
│   └── data_class/           # Data class tests
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## TODO
- Add solving with rating function **DONE**
- Add solving functions using OR
- Add student votes (parser, problem, rating function)
- Add end to end test
- Add celery
- Update README
- Algorithm optimization (rating function) not yet implemented
  for example if we test algorithm works then maybe we could have unsecure 
  (wouldnt check if we can insert the allocation) copies of inserting/deleting functions
- Allow for course not being present in definition (care for output)
