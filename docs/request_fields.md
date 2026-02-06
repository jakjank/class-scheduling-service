## Objects expected in request

The value of each field of the request, except `method`, is a list of objects which indirectly define constraints which must be met by the solution.
Below we explain what should a value of each field in the request be.

### Method
The value of this field (string) specifies which algorithm should be used by the service to find the allocations for groups or how much information user wants to get when checking the allocations. Proper values when sending request to `/schedule` endpoint are:
* `"probabilistic_alg"`,
* `"ordered_groups_alg"`,
* `"deep_ordered_groups_alg"`,
* and `"rating_function_alg"`

Proper values when sending request to `/check` endpoint are:
* `"simple_check"` - service looks for a failed constraint. If finds one then it stops further checking and sends the response back
* `"full_check"`- service looks for ALL failed constraints. Response contains (in the `msg` filed) list of all failed constraints

If value other than listed above (per endpoint) is passed then the service will not do anything beyond returning message informing about this. To learn more about algorithms checkout [algorithms desription](algorithms.md)

### Teachers
This field is a list of *Teacher* objects. The role of **Teacher** object is to represent real human availability.
**Teacher** object consists of following fields:
* id - the lecturer's unique identifier
* availability - a dictionary representing the slots per day in which the teacher is available. Days are keys and are in ISO-8601 format (1 is monday, 7 is sunday). The values in the dictionary are lists of natural numbers representing time slots. The mapping of individual slots to real time slots is not imposed by the system and can be freely interpreted by the user. One may consider slot 0 to mean 7:30-8:15 time slot, 1 to mean 8:25-9:10 and so on and other may consider 8 to mean 8:00-9:00, 9 to mean 9:00-10:00 etc. In below and each next of the examples we will use the second interpretation. The numbers indicating slots must be non-negative and next slots must be referenced by next natural numbers. It is user's responsibility to use the same interpretation consistently across the whole request.

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

### Rooms
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
### Groups
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

### Clusters
List of **Cluster** objects. A **Cluster** is an object that defines time relationship between group assigments. It enables the user to require some groups to take time in the same time blocks or not to overlap at all. **Cluster** consists of the following fields:

* group_ids - a list of group IDs whose assignments must satisfy the cluster
* range - the number and length (in slots) of blocks in which groups must take place. Blocks do not have to appear in timetable in the order in which they are stored in *range* and can take place on the same or different days. If the range is an empty list then the groups realization times cannot overlap

The following example means that groups with IDs 11, 12, 13, and 14 must be held in two time blocks. The first block is two slots long, and the second one is four slots long.

```json
{
"group_ids": [11, 12, 13, 14],
"range": [2, 4]
}
```

### Allocations
This field is a list of **Allocation** objects. **Allocation** object defines an assigment of a group to the time and place. The response on succesfull request to `/schedule` endpoint also contains allocations in such form. The user may send self established assigments in **allocations** field of a request. In such situation the service will first check if these assigments are correct and if so, it will try to create a plan with these allocations. Allocation object consist of the following fields:
* group_id - a unique group identifier for which assigment is made
* room_ids - a list of room IDs where the given class is to be held
* day - the day the given class is to be held (in format consisent with ISO-8601)
* slots - list of time slots when class takes place

For example, the allocation object below means that the group with $id=1$ with assigned room with $id$ 32 and takes time on Fridays between 9:00 a.m. and 11:00a.m.
```json
{
    "group_id": 1,
    "room_ids": [32],
    "day": 5,
    "slots": [9,11]
}
```