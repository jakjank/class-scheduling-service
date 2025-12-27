import unittest
from backend.src import Group, Cluster, Availability

class TestGroup(unittest.TestCase):
    def test_from_json(self):
        data = """
        {
            "id": 32,
            "course_id": 17,
            "duration": 2,
            "capacity": 24,
            "availability": {"mon": [8,9,10,11], "fri": [12,13]},
            "labels": [["LAB"], ["CLASS", "TV"]],
            "teacher_ids": [2, 17]
        }
        """
        
        group = Group.from_json(data)

        self.assertEqual(group.id, 32)
        self.assertEqual(group.course_id, 17)
        self.assertEqual(group.duration, 2)
        self.assertEqual(group.capacity, 24)
        self.assertEqual(group.availability.hours, {'mon': [8,9,10,11], 
                                                      'tue': [],
                                                      'wed': [],
                                                      'thu': [],
                                                      "fri": [12,13],
                                                      'sat': [],
                                                      'sun': []})
        self.assertEqual(
            group.labels,
            [["LAB"], ["CLASS", "TV"]]
        )
        self.assertEqual(
            group.teacher_ids,
            [2,17]
        )
        self.assertEqual(group.period_mask, [])

    def test_from_json_with_period_mask(self):
        data = """
        {
            "id": 32,
            "course_id": 17,
            "duration": 2,
            "capacity": 24,
            "availability": {"mon": [8,9,10,11], "fri": [12,13]},
            "labels": [["LAB"], ["CLASS", "TV"]],
            "teacher_ids": [2, 17],
            "period_mask": [1, 2, 7]
        }
        """
        
        group = Group.from_json(data)

        self.assertEqual(group.id, 32)
        self.assertEqual(group.course_id, 17)
        self.assertEqual(group.duration, 2)
        self.assertEqual(group.capacity, 24)
        self.assertEqual(group.availability.hours, {'mon': [8,9,10,11], 
                                                      'tue': [],
                                                      'wed': [],
                                                      'thu': [],
                                                      "fri": [12,13],
                                                      'sat': [],
                                                      'sun': []})
        self.assertEqual(
            group.labels,
            [["LAB"], ["CLASS", "TV"]]
        )
        self.assertEqual(
            group.teacher_ids,
            [2,17]
        )
        self.assertEqual(group.period_mask, [1,2,7])

    def test_adding_cluster(self):

        group = Group(32, 17, 2, 24, Availability({}), [], [], [])
        cluster = Cluster([2,2], [32,37])

        group.add_cluster(cluster)

        self.assertEqual(group.clusters, [cluster])