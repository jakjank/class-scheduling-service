import unittest
from backend.src import Parser

class TestParser(unittest.TestCase):
    def test_parsing_check_request(self):
        data = """
        {
            "requestType" : 0,
            "option": 1,
            "courses": [
                {  
                    "id": 1,
                    "name": "Logika dla informatyków"
                },
                {  
                    "id": 17,
                    "name": "MDM"
                }
            ],
            "groups": [
                {
                    "id": 1,
                    "course_id": 1,
                    "duration": 2,
                    "capacity": 24,
                    "availability": {"mon": [8,9,10,11], "fri": [12,13]},
                    "labels": [["CLASS"]],
                    "teacher_ids": [1, 2, 3]
                },
                {
                    "id": 2,
                    "course_id": 1,
                    "duration": 2,
                    "capacity": 24,
                    "availability": {"mon": [8,9,10,11], "fri": [12,13]},
                    "labels": [["CLASS"]],
                    "teacher_ids": [1, 2, 3]
                },
                {
                    "id": 3,
                    "course_id": 17,
                    "duration": 2,
                    "capacity": 30,
                    "availability": {"mon": [8,9,10,11], "fri": [12,13]},
                    "teacher_ids": [3,4]
                }
            ],
            "clusters": [
                {
                    "range": [2],
                    "groups_ids": [1, 2]
                }
            ],
            "rooms": [
                {
                    "id" : 32,
                    "capacity" : 24,
                    "availability" : {
                        "mon": [],
                        "tue": [10,11,12,13,14,15,16],
                        "wed": [],
                        "thu": [18,19],
                        "fri": [8,9,10,11,12],
                        "sat": [],
                        "sun": []
                        },
                    "labels" : ["CLASS", "TV"]
                }
            ],
            "teachers": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "quota": 10,
                    "availability": {"mon": [8,9,10,11], "fri": [12,13]}
                },
                {
                    "id": 2,
                    "name": "Jan Łania",
                    "quota": 20,
                    "availability": {"mon": [10,11]}
                },
                {
                    "id": 3,
                    "name": "Adam Kowalski",
                    "quota": 90,
                    "availability": {"mon": [8,9,10,11,12,13]}
                },
                {
                    "id": 4,
                    "name": "Ignacy Krajan",
                    "quota": 90,
                    "availability": {"fri": [12,13]}
                }
            ],
            "records": [
                {
                    "group_id": 1,
                    "teachers_ids": [2, 3],
                    "rooms_ids": [32],
                    "time_day": "fri",
                    "time_hour": 12 
                }
            ]
        }
        """
        
        parser = Parser()
        request = parser.parse(data)

        # request type
        self.assertEqual(request.request_type, 0)

        # Option
        self.assertEqual(request.option, 1)

        problem = request.problem

        # Courses
        self.assertEqual(len(problem.courses), 2)
        self.assertEqual(problem.courses[1].id, 1)
        self.assertEqual(problem.courses[1].name, "Logika dla informatyków")
        self.assertEqual(problem.courses[17].id, 17)
        self.assertEqual(problem.courses[17].name, "MDM")

        # Groups
        self.assertEqual(len(problem.groups), 3)
        g1 = problem.groups[1]
        self.assertEqual(g1.id, 1)
        self.assertEqual(g1.course_id, 1)
        self.assertEqual(g1.duration, 2)
        self.assertEqual(g1.capacity, 24)
        self.assertEqual(g1.teacher_ids, [1, 2, 3])
        self.assertEqual(g1.labels, [["CLASS"]])

        g3 = problem.groups[3]
        self.assertEqual(g3.course_id, 17)
        self.assertEqual(g3.teacher_ids, [3, 4])
        self.assertEqual(g3.capacity, 30)
        self.assertEqual(g3.labels, [])

        c1 = problem.clusters[0]
        self.assertEqual(c1.range, [2])
        self.assertEqual(c1.groups_ids, [1, 2])

        # Rooms
        self.assertEqual(len(problem.rooms), 1)
        r = problem.rooms[32]
        self.assertEqual(r.id, 32)
        self.assertEqual(r.capacity, 24)
        self.assertIn("CLASS", r.labels)
        self.assertIn("TV", r.labels)
        self.assertEqual(r.availability.hours["tue"], [10, 11, 12, 13, 14, 15, 16])
        self.assertEqual(r.availability.hours["thu"], [18,19])
        self.assertEqual(r.availability.hours["fri"], [8,9,10,11,12])
        self.assertTrue(all(r.availability.hours[h] == [] for h in ['mon', 'wed', 'sat', 'sun']))

        # Teachers
        self.assertEqual(len(problem.teachers), 4)
        t1 = problem.teachers[1]
        self.assertEqual(t1.id, 1)
        self.assertEqual(t1.name, "John Doe")
        self.assertEqual(t1.quota, 10)
        self.assertEqual(t1.availability.hours["mon"], [8, 9, 10, 11])
        self.assertEqual(t1.availability.hours["fri"], [12, 13])

        t2 = problem.teachers[2]
        self.assertEqual(t2.id, 2)
        self.assertEqual(t2.name, "Jan Łania")
        self.assertEqual(t2.quota, 20)
        self.assertEqual(t2.availability.hours["mon"], [10, 11])

        t3 = problem.teachers[3]
        self.assertEqual(t3.id, 3)
        self.assertEqual(t3.name, "Adam Kowalski")
        self.assertEqual(t3.quota, 90)
        self.assertEqual(t3.availability.hours["mon"], [8, 9, 10, 11, 12, 13])

        t4 = problem.teachers[4]
        self.assertEqual(t4.id, 4)
        self.assertEqual(t4.name, "Ignacy Krajan")
        self.assertEqual(t4.quota, 90)
        self.assertEqual(t4.availability.hours["fri"], [12, 13])

        # Records
        r1 = problem.records[0]
        self.assertEqual(r1.group_id, 1)
        self.assertEqual(r1.teachers_ids, [2, 3])
        self.assertEqual(r1.rooms_ids, [32])
        self.assertEqual(r1.day, "fri")
        self.assertEqual(r1.hour, 12)

        # Option
        self.assertEqual(request.option, 1)