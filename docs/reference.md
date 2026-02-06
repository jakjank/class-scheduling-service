# Code Reference

## Problem

Core class representing the problem to solve. Defined in `src/problem.py`.

### Functions

Most important methods of `Probem` class:

#### `check(self, method="simple_check") -> list[str]`
Function which checks if each group is allocated properly.
Parameters:
* **method** - Specifies if all failed contraints should be found (`full_check`) or if we just want to know if the allocations are correct - any faild constraint (`simple_check`)
Returns:
list of failed constraints (empty if everything is ok)

#### precheck(self)
Similar to the `check` function, but only checks if exisiting alocations are correct (there may be unallocated groups).
Returns:
list of failed constraints (empty if everything is ok)

#### `add_teacher(self, teacher: Teacher) -> None`
Adds `Teacher` object to the Problem. Raises an error if `Teacher` with the same `id` already exists.

#### `add_room(self, room: Room) -> None`
Adds `Room` object to the Problem. Raises an error if `Room` with the same `id` already exists.

#### `add_group(self, group: Group) -> None`
Adds `Group` object to the Problem. Raises an error if `Group` with the same `id` already exists.

#### `add_cluster(self, cluster: Cluster) -> None`
Adds `Cluster` object to the Problem. Raises an error if `Cluster` with the same `id` already exists.
It also looks for exisiting allocations of groups with ids in `cluster.group_ids`, and adds them to `cluster` internal list of allocations.

#### `add_allocation(self, allocation: Allocation) -> None`
Adds `Allocation` object to the Problem. Raises an error if `Allocation` with the same `group_id` already exists.
It also looks for exisiting cluster in which the `allocation.group_id` appears and adds `allocation` to found clusters lists of allocations.

#### `add_allocation_and_update_availability(self, allocation : Allocation) -> bool`
Checks if `allocation` can be added to the Problem. If yes, then it deletes availabilities of teachers teaching the group at the allocation time and the same for rooms.
Parameters:
**allocation** - `Allocation` object to be added to Problem.
Returns:
Boolean indicating if the allocation could be added or not.

## Parser

Object parsing and validating raw JSON requests to internal `Query`. Defined in `src/parser.py`

### Query

Internal class defined in `src/communication/query.py`. Represents parsed user request. consists of two fields:
* **problem** - object of `Problem` class
* **method** - string definig check type or algorithm to be used 

### Funtions

#### `parse(self, json_data: str, check_request=False) -> Query`
Gets the request as a row string and returns `Query`.
Parameters:
* **json_data** - request as a raw string
* **check_request** - boolean specifying if the request came to the `/schedule` or `/check` endpoint
Returns:
`Query` object

## Solver

Interface to the *Algorithms*. Defined in `src/solver`

### Response

Class defined in `src/communication/response.py`. It is the equivalent of object described in [API response format section](api.md#response_format)

### Functions

#### `solve(self, problem : Problem, method : str) -> Response`

Checks user defined allocations. Calls chosen algorithm. Checks the algorithm output and reterns the response. Raises an error if algorithm produced invalid solution.
Parameters:
* **problem** - instance of `Problem` class
* **method** - name of algorithm to be used (see [method field](request_fields.md#method))
Returns:
`Response` object

## Availability

Object describing availability of a resource (teacher, room, group). Defined in `src/models/availability.py`

### Fields

#### `slots`

The map of availible slots per day 
for example:
{2 : [5,6,7,8], 5 : [10,11]} means availability on Tuesday in slots 5,6,7, and 8 and on Friday in slots 10 and 11.

#### `taken_periods`

taken_periods dictionary stores the information about reservations made by groups with non empty occurrence_desc.

Format: (day, slot) -> list of ints

Example: 
If the teacher is to be reserved on Monday at slot 8 by group occuring every week then (if he is available at the time) the 8 is deleted from his availability[1].
But if the group with occurrence_desc = [1,3] wants to reserve the teacher at that time
the slot stays in availability[1], but 1 and 3 are added to taken_periods[(1,8)].
Then no other group with 1 or 3 or empty occurence_desc can reserve that teacher at that time.  

This variable provides a mechanism which enables 'sharing' of resources by groups occuring in different weeks.

### Functions

#### `from_json(json_string : str) -> Availability`

Parses raw string into Availability object. Raises an error in case of invalid data format.

#### `remove(self, day: int, slot: int, mask: list[int]) -> bool`

Checks if time is available and if so, removes it.
Parameters:
* **day** - integer defining the day
* **slot** - time slot to be removed
* **mask** - list of integers describig repeatability of the time to be reserved ([] - every week, [1,3] - weeks described by 1 and 3). (Result of [occurence_desc field](request_fields.md#groups))
Returns:
`True` if time was successfully removed, `False` otherwise

## Teacher

Equivalent of [teacher](request_fields.md#teachers). Defined in `src/models/teacher.py`

### Functions

#### `from_json(json_string : str) -> Teacher`

Parses raw string into Teacher object. Raises an error in case of invalid data format.

## Room

Equivalent of [room](request_fields.md#rooms). Defined in `src/models/room.py`

### Functions

#### `from_json(json_string : str) -> Room`

Parses raw string into Room object. Raises an error in case of invalid data format.

#### `satisfies_labels_DNF(self, labels_DNF: list[list[int]]) -> bool`

Checks if the label requirements to the room (described as elements of *labels* list in [group](request_fields.md#groups)) are satisfied by the room.
Parameters:
* **labels_DNF** - list of lists of labels. For example `[["TV", "whiteboard"], ["projector", "whiteboard"]]` means the room should have both `TV` and `whiteboard` labels or both `projector` and `whiteboard` labels.
Returns:
`True` if labels_DNF are satisfied by the room, `False` otherwise

## Group

Equivalen of [group](request_fields.md#groups). Defined in `src/models/group.py`

### Functions

#### `from_json(json_string : str) -> Group`

Parses raw string into Group object. Raises an error in case of invalid data format.

#### `are_labels_valid(labels: list) -> bool`

Checks if list of labels passed by the user in request has correct format.

## Cluster

Equivalent of [cluster](request_fields.md#clusters). Defined in `src/models/cluster.py`

### Functions

#### `from_json(json_string : str) -> Cluster`

Parses raw string into Cluster object. Raises an error in case of invalid data format.

#### `add_allocation(self, alloc: Allocation) -> None`

Adds `Allocation` object to the internal lists of allocations.

#### `check(self) -> bool`

Checks if allocations from internal list satisfy cluster's requiremens.

#### `can_use_slots(self, day: int, slots: list[int]) -> bool`

Checks if the allocation with given by `day` and `slots` can be added to the cluster so the `Cluster.check()` returns `True`.

## Allocation

Equivalent of [allocation](request_fields.md#allocations). Defined in `src/models/allocation.py`

### Functions

#### `from_json(json_str: str) -> Allocation`

Parses raw string into Allocation object. Raises an error in case of invalid data format.

## Utils 

In `algorithms/utils` functions shared by the algorithms are defined

### Functions

#### `get_all_placements_for_group(g : Group, prob : Problem) -> list[Allocation]:`

Finds all the possibe allocations for group in a given problem
Parameters:
* **g** - group for which we want to find allocations
* **prob** - `Problem` instance
Returns:
list of `Allocation`s

#### `get_best_allocation(placements : list[Allocation], prob : Problem, rating_function) -> Allocation`

Returns one of the *best* allocations based on the rating function.
Parameters:
* **placements** - list produced by `get_all_placements_for_group`
* **prob** - `Problem` instance
* **rating_function** - function which gets `Allocation` and `Problem` instances and returns the score of the given allocation. The bigger score the better allocation is.
Returns:
`Allocation` instance

#### `number_of_possible_placements(g : Group, prob : Problem) -> int`

Gets `Problem` instance and one `Group` from this problem and return the numbr of exisiting allocations for the group.

## Running Tests

Tests from `test_big_problem.py` may occasionally fail since the algorithms are probabilistic.

### If everything is installed locally

Run all tests:
```bash
python3 -m unittest discover .
```

Run specific test:
```bash
python3 -m unittest tests.test_problem.TestProblem.test_check_teacher_conflicts
```
### In running Docker container

1. Build and start the container
2. In second terminal get the *container_id*. Run:
```bash
docker ps
```
and copy *container_id* of container running on *solver* image (or however you named the image).
3. Run the tests:
```bash
docker exec container_id python3 -m unittest discover .
```
