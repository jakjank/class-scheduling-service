**Table of Contents**
* [A short introduction to scheduler](#short-introduction-to-scheduler)
  * [Quick start](#quick-start)
    * [Requirements](#requirements)
    * [Running the scheduler](#running-the-scheduler)
  * [Interacting with scheduler](#interacting-with-scheduler)
    * [Usage example](#usage-example)
  * [Documentation](#documentation)
  * [Project Structure](#project-structure)

# Short introduction to scheduler

Scheduler is a backend service for creating and validating timetables for educational institutions while respecting a variety of constraints, such as:
* Teacher availability
* Room types and capacities
* Relative start times of classes
* And several other scheduling rules

The service is designed primarily as a backend for timetable editors with a user-friendly UI, but it can also be used as a standalone application.

## Quick start

The project is written in Python and built with FastAPI and Uvicorn.
You can run it either:
* Directly with Python, or
* Inside a Docker container (recommended)

### Requirements

* **Python** 3.11.x
* **FastAPI** 0.128.x
* **Uvicorn** 0.40.x

You may install all dependencies manually, but using Docker is strongly recommended for a simpler and more reproducible setup.
To build the Docker image, navigate to the root directory of the project and run:
```bash
$ docker build -t scheduler
```

### Running the Scheduler

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

## Interacting with scheduler

The scheduler exposes two endpoints:

- POST /schedule — generate a timetable
- POST /check — verify a timetable

Queries and responses are JSON-based.

See detailed API documentation:
- [API Reference](docs/api.md)

### Usage Example

Sometimes an example is the best explanation. Here we have one to see how everything should work like:

```bash
curl -X POST http://localhost:7999/schedule \
-H "Content-Type:application/json" \
-d '
{
    "method": "rating_function_alg",
    "groups": [
        {
            "id": 1,
            "course_id": 1,
            "duration": 2,
            "capacity": 24,
            "availability": {
                "1": [8,9,10,11],
                "5": [12,13]
            },
            "labels": [[["pracownia"]]],
            "teacher_ids": [1]
        },
        {
            "id": 2,
            "course_id": 1,
            "duration": 2,
            "capacity": 24,
            "availability": {
                "1": [8,9,10,11],
                "5": [12,13]
            },
            "labels": [[["pracownia"]]],
            "teacher_ids": [1]
        }
    ],
    "clusters": [
        {
			"id": 1,
            "group_ids": [1, 2],
            "range": [4]
        }
    ],
    "rooms": [
        {
            "id" : 32,
            "capacity" : 24,
            "availability" : {
                "1": [8,9,10,11,12,13,14,15,16],
                "2": [8,9,10,11]
            },
            "labels" : ["pracownia", "linux"]
        }
    ],
    "teachers": [
        {
            "id": 1,
            "availability": {
                "1": [8,9,10,11],
                "5": [8,9,10,11,12,13]
            }
        }
    ],
    "allocations": [
        {
            "group_id": 1,
            "room_ids": [32],
            "day": 1,
            "slots": [8,9] 
        }
    ]
}'
```

Above request should return:

```json
{
    "success": true,
    "errors": [],
    "solution": [
        {
            "group_id": 1,
            "room_ids": [32],
            "day": 1,
            "slots": [8,9]
        },
        {
            "group_id": 2,
            "room_ids": [32],
            "day": 1,
            "slots": [10,11]
        }
    ]
}
```

We might like to check if group with id 2 could start at slot 11. To do so we should send next request to **/check** endpoint with such change in **allocations** and the rest of data as before:

```bash
curl -X POST http://localhost:7999/check \
-H "Content-Type:application/json" \
-d '{
    // other data as before
    "allocations": [
        {
            "group_id": 1,
            "room_ids": [32],
            "day": 1,
            "slot": 8
        },
        {
            "group_id": 2,
            "room_ids": [32],
            "day": 1,
            "slot": 11 //zmiana z 10 na 11
        }
    ]
}'
```

For such request we will get following response:

```json
{
    "success": false,
    "errors": [
        {
            "type": "cluster",
            "id": 1,
            "msg:": "Cluster connecting groups with ids 1, 2 is not satisfied"
        }
    ],
    "solution": []
}
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [API Reference](docs/api.md)
- [Detailed request fields desription Model](docs/request_fields.md)
- [Definition of assigments correctness](docs/correctness.md)
- [Architecture](docs/architecture.md)
- [Code reference](docs/reference.md)
