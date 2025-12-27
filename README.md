# Backend for YAPA

Backend for the YAPA (Yet Another Planning Asisstant) timetable scheduling system. The backend solves and validates university course scheduling constraints, ensuring teachers, rooms, and groups are optimally assigned while respecting availability, capacity, and clustering requirements.

## Overview

The backend is built with **FastAPI** and provides an HTTP API for solving timetable scheduling problems described in JSON format. It listens on **port 7999** and accepts constraint-based scheduling problems, returning either a valid solution or constraint violation information.

## API Interface

### Endpoints

#### `POST /solve`

Accepts a scheduling problem and returns a JSON response with the solution or error information.

### Request Format

The request should be a JSON object with the following structure:

```json
{
  "requestType": 0,
  "option": 1,
  "courses": [...],
  "groups": [...],
  "teachers": [...],
  "rooms": [...],
  "clusters": [...]
  "established": [...]
}
```

**Request Types:**
- `requestType: 0` - **Solve Request**: Find a complete timetable solution
- `requestType: 1` - **Check Request**: Validate pre-made assignments against constraints

**Options:**
- 0 - makes solver use algortihm with random placement of groups
- 1 - makes solve use `"randomOrdered"` algorithm
- 2 - makes solver use `"withRatingFunction"` algorithm

### Constraints Format

#### Courses
```json
{
  "id": 1,
  "name": "Logika dla informatyków"
}
```

#### Groups (Classes/Labs)
```json
{
  "id": 1,
  "course_id": 1,
  "duration": 2,
  "capacity": 24,
  "availability": {
    "mon": [8, 9, 10, 11],
    "fri": [12, 13]
  },
  "labels": [["CLASSROOM"], ["LAB"]],
  "teacher_ids": [1, 2, 3],
  "period_mask": [1, 3]
}
```

**Fields:**
- `id`: Unique identifier
- `course_id`: Associated course
- `duration`: Class duration in hours (e.g., 2 means 2-hour block)
- `capacity`: Maximum students
- `availability`: Hours available per day (e.g., `[10, 11, 12]` means hours 10:00-11:00, 11:00-12:00, 12:00-13:00)
- `labels`: Required room features (nested lists for alternative requirements)
- `teacher_ids`: Assigned teachers
- `period_mask`: Semester weeks (e.g., `[1, 3]` for odd weeks only; empty = all weeks)

#### Teachers
```json
{
  "id": 1,
  "name": "John Doe",
  "quota": 90,
  "availability": {
    "mon": [8, 9, 10, 11],
    "fri": [12, 13]
  },
  "taken_periods": []
}
```

**Fields:**
- `id`: Unique identifier
- `name`: Teacher name
- `quota`: Maximum hours per semester (reference only)
- `availability`: Hours available per day
- `taken_periods`: Pre-reserved week periods (conflicts with group's `period_mask`)

#### Rooms
```json
{
  "id": 32,
  "capacity": 24,
  "availability": {
    "mon": [],
    "tue": [10, 11, 12, 13, 14, 15, 16],
    "wed": [],
    "thu": [18, 19],
    "fri": [8, 9, 10, 11, 12],
    "sat": [],
    "sun": []
  },
  "labels": ["CLASSROOM", "TV"],
  "taken_periods": []
}
```

**Fields:**
- `id`: Unique identifier
- `capacity`: Room capacity
- `availability`: Hours available per day
- `labels`: Room features (e.g., "TV", "PROJECTOR", "LAB")
- `taken_periods`: Pre-reserved week periods

#### Clusters
Groups can be constrained to share certain time slots. For example, all lectures of a course should be on the same day.

```json
{
  "range": [2, 4],
  "groups_ids": [1, 2, 3]
}
```

**Fields:**
- `range`: Time block requirements (e.g., `[2, 4]` means groups occupy one 2-hour block and one 4-hour block)
- `groups_ids`: Group IDs affected by this constraint

#### Established (Pre-made Assignments)
```json
[
  {
    "group_id": 1,
    "teachers_ids": [1, 2],
    "rooms_ids": [32],
    "day": "mon",
    "hour": 10
  }
]
```

These are hardcoded assignments that must be included in the solution They have to satisfy contraints.

### Response Format

#### Success Response
```json
{
  "status": 0,
  "msg": "Solution found",
  "solution": [
    {
      "group_id": 1,
      "teachers_ids": [1, 2],
      "rooms_ids": [32],
      "day": "mon",
      "hour": 10
    },
    ...
  ]
}
```

#### Error Response
```json
{
  "status": 1,
  "msg": "Error details",
  "solution": []
}
```

**Status Codes:**
- `0` - Solution found successfully
- `1` - Error (check message field for details)

## Data Classes

### Core Classes

**Availability**
- `hours`: Dictionary mapping days to available hours
  - Example: `{"mon": [10, 11, 12], "fri": [14, 15]}`
  - Represents hours 10:00-11:00, 11:00-12:00, 12:00-13:00 on Monday, etc.

**Cluster**
- `range`: List of time block sizes (in hours)
- `groups_ids`: List of group IDs constrained together
- Example: Groups must fit into `[2, 4]` = one 2-hour and one 4-hour block

**Course**
- `id`: Unique identifier
- `name`: Course name

**Group**
- `id`: Unique identifier
- `course_id`: Associated course
- `duration`: Class duration in hours
- `capacity`: Maximum students
- `availability`: Availability map
- `labels`: Required room features (lists for alternatives)
- `teacher_ids`: Assigned teacher IDs
- `period_mask`: Allowed semester weeks

**Record**
- `group_id`: Associated group ID
- `teachers_ids`: Assigned teacher IDs
- `rooms_ids`: Assigned room IDs
- `day`: Day of week (mon-sun)
- `hour`: Start hour (0-23)

**Room**
- `id`: Unique identifier
- `capacity`: Room capacity
- `availability`: Availability map
- `labels`: Room features (strings)
- `taken_periods`: Pre-reserved weeks

**Teacher**
- `id`: Unique identifier
- `name`: Teacher name
- `quota`: Maximum hours (reference)
- `availability`: Availability map
- `taken_periods`: Pre-reserved weeks

**SyncCluster** (not currently used)

## Core Logic Classes

### Parser
- **Method**: `parse(json_data: str) -> Request`
- Converts JSON input into Python Problem objects
- Validates and deserializes all constraint objects
- Returns a `Request` object containing problem and algorithm choice

### Problem
- **Responsibilities**:
  - Store all constraints (teachers, rooms, groups, courses, clusters, records)
  - Validate constraints against each other
  - Track established (hardcoded) assignments
  - Provide constraint checking methods

- **Key Methods**:
  - `add_teacher()`, `add_room()`, `add_group()`, etc. - Add entities
  - `check()` - Validate complete solution against all constraints
  - `check_established()` - Validate pre-made assignments
  - `check_teacher_availability()` - Verify teacher availability
  - `check_room_availability()` - Verify room availability
  - `check_cluster_constraints()` - Verify cluster requirements
  - And more constraint validation methods...

### Solver
- **Responsibilities**:
  - Find valid timetable solutions using various algorithms
  - Return `Response` object with status and solution

- **Methods**:
  - `solve(problem, option)` - Main entry point (dispatches to algorithm)
  - `random_solve()` - Random placement algorithm
  - `random_ordered_groups_solve()` - Ordered random placement
  - `with_rating_function_solve()` - TODO: Optimized algorithm

### Utility Functions
- `covers(hours, start, duration)` - Check if time range is covered
- `check_period_mask(needed, taken)` - Validate week constraints
- `is_cluster_satisfied(cluster, triples)` - Verify cluster satisfaction
- `check_clustering(group, day, hour, duration, problem)` - Validate new assignment against clusters
- `get_all_placements_for_group(group, problem)` - Find valid placements for a group

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Start the FastAPI server:

```bash
python3 main.py
```

The server will start on `http://0.0.0.0:7999`

## Running Tests

Run all backend tests:

```bash
python3 -m unittest discover -s backend/tests -v
```

Run specific test:

```bash
python3 -m unittest backend.tests.test_utils.TestUtils.test_is_cluster_satisfied -v
```

## Project Structure

```
backend/
├── src/
│   ├── __init__.py           # Module exports
│   ├── parser.py             # JSON parser
│   ├── problem.py            # Problem definition and constraints
│   ├── solver.py             # Solver algorithms
│   ├── utils.py              # Utility functions
│   └── data_class/           # Data models
│       ├── availability.py
│       ├── cluster.py
│       ├── course.py
│       ├── group.py
│       ├── record.py
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

## Algorithm Details

### Random Solve
- Randomly shuffles groups, teachers, and rooms
- For each unscheduled group, finds all valid placements
- Randomly selects one valid placement
- Repeats until all groups are scheduled or no valid placement exists

### Cluster Constraints
Groups can be clustered to share time patterns. The `is_cluster_satisfied()` function:
- For each day with cluster groups, calculates total time span
- Tries to match spans with cluster block sizes
- Supports multiple blocks per day when needed
- Adjacent classes can use separate blocks if a single block can't accommodate the span

## TODO
- Add solving with rating function **DONE**
- implement rating function
- Add solving functions using OR
- Add student votes (parser, problem, rating function)
- Add end to end test
- Add celery
- make `get_all_placement_for_group` return not placements witout squashed rooms?
- Refactor (divide utils, think about architecture)
- Improve error messages and logging
- cleanup imports, __init__s
- Update README
- Algorithm optimization (rating function) not yet implemented
  for example if we test algorithm works then maybe we could have unsecure 
  (wouldnt check if we can insert the record) copies of inserting/deleting functions