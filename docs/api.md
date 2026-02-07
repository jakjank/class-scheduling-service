
## Endpoints

The scheduler offers two HTTP endpoints to which you can POST your requests:

* `/schedule` - Accepts a scheduling problem and returns a JSON response with the solution or error information.
* `/check` - Accepts a scheduling problem and returns a JSON response with confirmation or deny of correctness of sent assigments

## Query schema

The request, endpoint does not matter, should be a JSON object with the following structure:

```json
{
  "method":      "specification",
  "teachers":    [...],
  "rooms":       [...],
  "groups":      [...],
  "clusters":    [...],
  "allocations": [...]
}
```

The value of each field of the request, except `method`, is a list of objects which indirectly define constraints which must be met by the solution.

See detailed request fields description:
- [Fields description](request_fields.md)

## Response Format

Response is JSON based and has the following structure:

```json
{
    "success": false,
    "errors": [],
    "solution": []
}
```

After sending a query to the solver, it returns a response in JSON format. It consists of three fields:
* **success** - Boolean indicating the success or failure of the query. In the case of a query to generate a solution (the query was sent to `/schedule` endpoint), failure means that the schedule could not be generated. In the case of a query to verify the solution (the query was sent to `/check` endpoint), failure means that the group assignments submitted in the *allocations* field do not satisfy the specified constraints
* **errors** - List of **issues** sent by the solver. It may indicate a logical or semantic error in the submitted data, describe a problem encountered while generating or checking the schedule. If the request was sent to the `/check` endpoint and was correct the value of this field is a list of descriptions of failed contraints. Format of **issue** is descibed below.
* **solution** - A list of allocations in the same format as the query. If *status* = 0 for the query to generate a schedule, this list contains the assignments of all groups; if *status* = 1, this list is empty. If the query was about the correctness of the solution and the sent allocations satisfied the constraints, then the returned value in the *solution* field has the same allocations as the *allocations* field in the query, otherwise the value of the *solution* field is "[]"

### Issue schema

An **issue** is a dictionary with:
* *type* of the error, 
* *id* of the element which caused the error (may be 0 for example if it was runtime error caused by bad query),
* and *msg* which has some extra informations

Examples:
```json
{
   "type": "allocation",
   "id": 1,
   "msg:": "Group with id=1 cannot take place on 1 in slots [8, 9]"
}

{
   "type": "other",
   "id": 0,
   "msg:": "Failed precheck. Given assignments do not satisfy constraints."
}
```