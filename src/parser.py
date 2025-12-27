from .problem import Problem
from .data_class import *
import json

class Request:
    def __init__(self, req_type: int, problem: Problem, option: int):
        self.request_type = req_type
        self.problem = problem
        self.option = option

class Parser:
    def parse(self, json_data:str) -> Request:
        problem = Problem()
        data = json.loads(json_data)

        req_type = data.get("requestType")

        if(req_type == 0):
            option = data.get("option") #who handles errors here?

        for course in data.get('courses', []):
            problem.add_course(Course.from_json(json.dumps(course)))
        for room in data.get('rooms', []):
            problem.add_room(Room.from_json(json.dumps(room)))
        for group in data.get('groups', []):
            problem.add_group(Group.from_json(json.dumps(group)))
        for teacher in data.get('teachers', []):
            problem.add_teacher(Teacher.from_json(json.dumps(teacher)))
        for cluster in data.get('clusters', []):
            problem.add_cluster(Cluster.from_json(json.dumps(cluster)))
        
        established = data.get("records", [])
        for record in established:
            problem.add_record(Record.from_json(json.dumps(record)))

        return Request(req_type, problem, option)
