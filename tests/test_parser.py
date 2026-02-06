from src import Parser
from src.models import Group
import unittest

class TestParser(unittest.TestCase):
    def test_parsing_request(self):
        data = """
        {
            "method": "probabilistic_alg",
            "groups": [
                {
                    "id": 1,
                    "duration": 2,
                    "capacity": 24,
                    "availability": {"1": [8,9,10,11], "5": [12,13]},
                    "labels": [[["CLASS"]]],
                    "teacher_ids": [1, 2, 3]
                },
                {
                    "id": 2,
                    "duration": 2,
                    "capacity": 24,
                    "availability": {"1": [8,9,10,11], "5": [12,13]},
                    "labels": [[["CLASS"]]],
                    "teacher_ids": [1, 2, 3]
                },
                {
                    "id": 3,
                    "duration": 2,
                    "capacity": 30,
                    "availability": {"1": [8,9,10,11], "5": [12,13]},
                    "teacher_ids": [3,4]
                }
            ],
            "clusters": [
                {
                    "id": 1,
                    "range": [2],
                    "group_ids": [1, 2]
                }
            ],
            "rooms": [
                {
                    "id" : 32,
                    "capacity" : 24,
                    "availability" : {
                        "1": [],
                        "2": [10,11,12,13,14,15,16],
                        "3": [],
                        "4": [18,19],
                        "5": [8,9,10,11,12],
                        "6": [],
                        "7": []
                        },
                    "labels" : ["CLASS", "TV"]
                }
            ],
            "teachers": [
                {
                    "id": 1,
                    "availability": {"1": [8,9,10,11], "5": [12,13]}
                },
                {
                    "id": 2,
                    "availability": {"1": [10,11]}
                },
                {
                    "id": 3,
                    "availability": {"1": [8,9,10,11,12,13]}
                },
                {
                    "id": 4,
                    "availability": {"5": [12,13]}
                }
            ],
            "allocations": [
                {
                    "group_id": 1,
                    "room_ids": [32],
                    "day": 5,
                    "slots": [12,13] 
                }
            ]
        }
        """
        
        parser = Parser()
        request = parser.parse(data)

        # Option
        self.assertEqual(request.method, "probabilistic_alg")

        problem = request.problem

        # Groups
        self.assertEqual(len(problem.groups), 3)
        g1 = problem.groups[1]
        self.assertEqual(g1.id, 1)
        self.assertEqual(g1.duration, 2)
        self.assertEqual(g1.capacity, 24)
        self.assertEqual(g1.teacher_ids, [1, 2, 3])
        self.assertEqual(g1.labels, [[["CLASS"]]])

        g3 = problem.groups[3]
        self.assertEqual(g3.teacher_ids, [3, 4])
        self.assertEqual(g3.capacity, 30)
        self.assertEqual(g3.labels, [])

        c1 = problem.clusters[0]
        self.assertEqual(c1.id, 1)
        self.assertEqual(c1.range, [2])
        self.assertEqual(c1.group_ids, [1, 2])

        # Rooms
        self.assertEqual(len(problem.rooms), 1)
        r = problem.rooms[32]
        self.assertEqual(r.id, 32)
        self.assertEqual(r.capacity, 24)
        self.assertIn("CLASS", r.labels)
        self.assertIn("TV", r.labels)
        self.assertEqual(r.availability.slots[2], [10, 11, 12, 13, 14, 15, 16])
        self.assertEqual(r.availability.slots[4], [18,19])
        self.assertEqual(r.availability.slots[5], [8,9,10,11,12])
        self.assertTrue(all(r.availability.slots[h] == [] for h in [1, 3, 6, 7]))

        # Teachers
        self.assertEqual(len(problem.teachers), 4)
        t1 = problem.teachers[1]
        self.assertEqual(t1.id, 1)
        self.assertEqual(t1.availability.slots[1], [8, 9, 10, 11])
        self.assertEqual(t1.availability.slots[5], [12, 13])

        t2 = problem.teachers[2]
        self.assertEqual(t2.id, 2)
        self.assertEqual(t2.availability.slots[1], [10, 11])

        t3 = problem.teachers[3]
        self.assertEqual(t3.id, 3)
        self.assertEqual(t3.availability.slots[1], [8, 9, 10, 11, 12, 13])

        t4 = problem.teachers[4]
        self.assertEqual(t4.id, 4)
        self.assertEqual(t4.availability.slots[5], [12, 13])

        # Allocations
        r1 = problem.allocations[0]
        self.assertEqual(r1.group_id, 1)
        self.assertEqual(r1.room_ids, [32])
        self.assertEqual(r1.day, 5)
        self.assertEqual(r1.slots, [12,13])

        # Option
        self.assertEqual(request.method, "probabilistic_alg")

    def test_parser_return_descriptive_errors(self):
        data = """
        {
            "method": "probabilistic_alg",
            "courses": [
                {  
                    "id": 1,
                    "name": "Logika dla informatyków"
                }
            ],
            "groups": [
                {
                    "id": 1,
                    "duration": "abc",
                    "capacity": 24,
                    "availability": {"1": [8,9,10,11], "5": [12,13]},
                    "labels": [[["CLASS"]]],
                    "teacher_ids": [1]
                }
            ],
            "rooms": [
                {
                    "id" : 32,
                    "capacity" : 24,
                    "availability" : {
                        "2": [10,11,12,13,14,15,16],
                        "4": [18,19],
                        "5": [8,9,10,11,12]
                        },
                    "labels" : ["CLASS", "TV"]
                }
            ],
            "teachers": [
                {
                    "id": 1,
                    "availability": {"1": [8,9,10,11], "5": [12,13]}
                }
            ]
        }
        """
        
        parser = Parser()

        with self.assertRaises(ValueError) as err:
            parser.parse(data)

        self.assertIn("duration", str(err.exception))
        self.assertIn("abc", str(err.exception))

    def test_parser_throws_when_group_has_no_teachers(self):
        data = """
        {
            "method": "probabilistic_alg",
            "groups": [
                {
                    "id": 1,
                    "duration": 2,
                    "capacity": 24,
                    "availability": {"1": [8,9,10,11]},
                    "labels": [[["CLASS"]]],
                    "teacher_ids": []
                }
            ]
        }
        """
        
        parser = Parser()

        Group.THROW_IF_NO_TEACHER = True
        with self.assertRaises(ValueError) as err:
            parser.parse(data)

        self.assertIn("teacher", str(err.exception))
