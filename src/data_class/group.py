import json
from .cluster import Cluster
from .availability import Availability

class Group:
    def __init__(self, id:int, course_id:int, duration:int, capacity:int, availability:Availability, labels:list[list], teacher_ids:list[int], period_mask: list[int]):
        self.id = id
        self.course_id = course_id
        self.duration = duration
        self.capacity = capacity
        self.availability = availability
        self.labels = labels
        self.teacher_ids = teacher_ids
        if period_mask:
            self.period_mask = period_mask
        else:
            self.period_mask = []
        self.clusters = []

    @staticmethod
    def from_json(json_string : str) -> 'Group':
        data = json.loads(json_string)
        id = data.get('id')
        course_id  = data.get('course_id')
        duration = data.get('duration')
        capacity = data.get('capacity')
        availability_data = data.get("availability")
        if availability_data:
            avail = Availability(availability_data)
        else:
            avail = Availability()
        labels = data.get('labels', [])
        
        teacher_ids = data.get('teacher_ids')
        period_mask = data.get('period_mask')
        return Group(id, course_id, duration, capacity, avail, labels, teacher_ids, period_mask)
    
    def add_cluster(self, c: Cluster):
        self.clusters.append(c)