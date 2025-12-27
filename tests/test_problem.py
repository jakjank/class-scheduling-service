import unittest
from backend.src import *

class TestProblem(unittest.TestCase):
    def test_check_group_presence(self):
        problem = Problem()
        problem.add_course(Course(12, "Matematyka dyskretna M"))
        problem.add_group(Group(17, 12, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        response = problem.check()

        self.assertEqual(response, "Matematyka dyskretna M group with id=17 is not present in solution")

    def test_check_teacher_availability(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"thu" : [15, 16]}), [], [15], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_record(Record(17, [15], [5], "thu", 15))
        response = problem.check()

        self.assertEqual(response, "Teacher Jaś (id=15) is not available on thu between 15 and 17")

    def test_check_teacher_conflicts(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 3, 2, 30, Availability({}), [], [15], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_record(Record(18, [15], [6], "fri", 11))
        response = problem.check()

        self.assertIn(response, "Teacher Jaś (id=15) has conflicting classes on fri between 10 and 13")
    
    def test_check_room_availability(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_room(Room(5, 36, Availability({"thu" : [8,9]}), []))
        response = problem.check()

        self.assertEqual(response, "Room with id=5 is not available on fri between 10 and 12")

    def test_check_room_colission(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 2, 2, 30, Availability({"fri" : [10,11]}), [], [16], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_teacher(Teacher(16, "Krzyś", 90, Availability({"fri" : [10,11]})))
        problem.add_room(Room(5, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_record(Record(18, [16], [5], "fri", 11))
        response = problem.check()

        self.assertEqual(response, "At least two groups (id=17, id=18) use room(s) with id=5 in the same time on fri between 10 and 12")

    def test_check_room_labels(self):
        problem = Problem()
        problem.add_course(Course(12, "Matematyka dyskretna M"))
        problem.add_group(Group(17, 12, 2, 30, Availability({"fri" : [10,11]}), [["TV"]], [15], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_room(Room(5, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        response = problem.check()

        self.assertEqual(response, "Matematyka dyskretna M group with id=17 has room(s) with labels=[[]] but needs labels=[['TV']]")

    def test_check_room_capacity(self):
        problem = Problem()
        problem.add_course(Course(12, "Algebra"))
        problem.add_group(Group(17, 12, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_room(Room(5, 24, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        response = problem.check()

        self.assertEqual(response, "Algebra group with id=17 has capacity=30 but has assigned room (id=5) with capacity=24")

    def test_check_cluster_satisfaction_hourly(self):
        problem = Problem()
        problem.add_course(Course(12, "Algebra"))
        problem.add_group(Group(17, 12, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 12, 2, 30, Availability({"fri" : [10,11]}), [], [16], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_teacher(Teacher(16, "Krzyś", 90, Availability({"fri" : [10,11]})))
        problem.add_room(Room(5, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_room(Room(6, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_cluster(Cluster([2], [17,18]))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_record(Record(18, [16], [6], "fri", 12))
        response = problem.check()

        self.assertEqual(response, "Cluster connecting groups with ids 17, 18 is not satisfied")

    def test_check_cluster_satisfaction_daily(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 2, 2, 30, Availability({"fri" : [10,11]}), [], [16], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_teacher(Teacher(16, "Krzyś", 90, Availability({"fri" : [10,11]})))
        problem.add_room(Room(5, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_room(Room(6, 36, Availability({"thu" : [8,9,10,11,12]}), []))
        problem.add_cluster(Cluster([2], [17,18]))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_record(Record(18, [16], [6], "thu", 10))
        response = problem.check()

        self.assertEqual(response, "Cluster connecting groups with ids 17, 18 is not satisfied")

    def test_check_cluster_satisfaction_complicated(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 2, 2, 30, Availability({"fri" : [10,11,12,13], "thu" : [10,11]}), [], [16], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_teacher(Teacher(16, "Krzyś", 90, Availability({"fri" : [10,11,12,13], "thu" : [10,11]})))
        problem.add_room(Room(5, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_room(Room(6, 36, Availability({"thu" : [8,9,10,11,12]}), []))
        problem.add_cluster(Cluster([2,2], [17,18]))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_record(Record(18, [16], [6], "thu", 10))
        response = problem.check()

        self.assertEqual(response, "0")

    def test_check_cluster_satisfaction_complicated2(self):
        problem = Problem()
        problem.add_group(Group(17, 1, 2, 30, Availability({"fri" : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 2, 2, 30, Availability({"fri" : [10,11,12,13]}), [], [16], []))
        problem.add_teacher(Teacher(15, "Jaś", 90, Availability({"fri" : [10,11]})))
        problem.add_teacher(Teacher(16, "Krzyś", 90, Availability({"fri" : [10,11,12,13]})))
        problem.add_room(Room(5, 36, Availability({"fri" : [8,9,10,11,12]}), []))
        problem.add_room(Room(6, 36, Availability({"fri" : [8,9,10,11,12,13]}), []))
        problem.add_cluster(Cluster([2,2], [17,18]))
        problem.add_record(Record(17, [15], [5], "fri", 10))
        problem.add_record(Record(18, [16], [6], "fri", 12))
        response = problem.check()

        self.assertEqual(response, "0")
    
    def test_check_group_availability(self):
        problem = Problem()
        problem.add_course(Course(12, "Algebra"))
        problem.add_group(Group(17, 12, 2, 30, Availability({"thu" : [15, 16]}), [], [], []))
        problem.add_record(Record(17, [], [], "thu", 16))
        response = problem.check()

        self.assertEqual(response, "Algebra group with id=17 cannot take place on thu between 16 and 18")

    def test_add_record_and_update_availability_single_hour_no_mask(self):
        problem = Problem()
        teacher_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher = Teacher(1, "Prof. Smith", 40, teacher_avail)
        room = Room(101, 50, room_avail, [])
        group = Group(5, 1, 1, 30, Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [1], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        record = Record(5, [1], [101], 'mon', 10, [])
        result = problem.add_record_and_update_availability(record)
        
        self.assertTrue(result)
        self.assertEqual(teacher.availability.hours['mon'], [11, 12])
        self.assertEqual(room.availability.hours['mon'], [11, 12])
        self.assertIn(record, problem.records)

    def test_add_record_and_update_availability_multi_hour_no_mask(self):
        problem = Problem()
        teacher_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher = Teacher(2, "Dr. Jones", 40, teacher_avail)
        room = Room(102, 30, room_avail, [])
        group = Group(6, 1, 3, 25, Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [2], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        record = Record(6, [2], [102], 'mon', 10, [])
        result = problem.add_record_and_update_availability(record)
        
        self.assertTrue(result)
        # Should remove hours 10, 11, 12 (3 hour duration)
        self.assertEqual(teacher.availability.hours['mon'], [13])
        self.assertEqual(room.availability.hours['mon'], [13])
        self.assertIn(record, problem.records)

    def test_add_record_and_update_availability_with_mask(self):
        problem = Problem()
        teacher_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher = Teacher(3, "Prof. Brown", 40, teacher_avail)
        room = Room(103, 40, room_avail, [])
        group = Group(7, 1, 2, 35, Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [3], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        record = Record(7, [3], [103], 'mon', 10, [1, 3])
        result = problem.add_record_and_update_availability(record)
        
        self.assertTrue(result)
        # Hours should still exist but have taken_periods
        self.assertEqual(teacher.availability.hours['mon'], [10, 11, 12])
        self.assertEqual(room.availability.hours['mon'], [10, 11, 12])
        self.assertEqual(teacher.availability.taken_periods[('mon', 10)], [1, 3])
        self.assertEqual(teacher.availability.taken_periods[('mon', 11)], [1, 3])
        self.assertEqual(room.availability.taken_periods[('mon', 10)], [1, 3])
        self.assertEqual(room.availability.taken_periods[('mon', 11)], [1, 3])
        self.assertIn(record, problem.records)

    def test_add_record_and_update_availability_teacher_unavailable(self):
        problem = Problem()
        teacher_avail = Availability({'mon': [10, 11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher = Teacher(4, "Dr. White", 40, teacher_avail)
        room = Room(104, 50, room_avail, [])
        group = Group(8, 1, 2, 30, Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [4], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        # Teacher only available for hours 10-11, but class needs hours 11-12 (2 hours starting at 11)
        record = Record(8, [4], [104], 'mon', 11, [])
        result = problem.add_record_and_update_availability(record)
        
        # Should fail because hour 12 is not available for teacher
        self.assertFalse(result)
        self.assertNotIn(record, problem.records)

    def test_add_record_and_update_availability_room_unavailable(self):
        problem = Problem()
        teacher_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room_avail = Availability({'mon': [10, 11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher = Teacher(5, "Prof. Green", 40, teacher_avail)
        room = Room(105, 50, room_avail, [])
        group = Group(9, 1, 2, 30, Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [5], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        # Room only available for hours 10-11, but class needs hours 11-12 (2 hours starting at 11)
        record = Record(9, [5], [105], 'mon', 11, [])
        result = problem.add_record_and_update_availability(record)
        
        # Should fail because hour 12 is not available for room
        self.assertFalse(result)
        self.assertNotIn(record, problem.records)

    def test_add_record_and_update_availability_multiple_teachers_and_rooms(self):
        problem = Problem()
        teacher1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        teacher2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher1 = Teacher(6, "Prof. Black", 40, teacher1_avail)
        teacher2 = Teacher(7, "Dr. Gray", 40, teacher2_avail)
        room1 = Room(106, 30, room1_avail, [])
        room2 = Room(107, 30, room2_avail, [])
        group = Group(10, 1, 2, 50, Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [6, 7], [])
        
        problem.add_teacher(teacher1)
        problem.add_teacher(teacher2)
        problem.add_room(room1)
        problem.add_room(room2)
        problem.add_group(group)
        
        record = Record(10, [6, 7], [106, 107], 'mon', 10, [])
        result = problem.add_record_and_update_availability(record)
        
        self.assertTrue(result)
        # Both teachers should have hours 10, 11 removed
        self.assertEqual(teacher1.availability.hours['mon'], [12])
        self.assertEqual(teacher2.availability.hours['mon'], [12])
        # Both rooms should have hours 10, 11 removed
        self.assertEqual(room1.availability.hours['mon'], [12])
        self.assertEqual(room2.availability.hours['mon'], [12])
        self.assertIn(record, problem.records)

    def test_add_record_and_update_availability_conflicting_mask(self):
        problem = Problem()
        teacher_avail = Availability(
            {'mon': [10, 11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []},
            {('mon', 10): [1, 3]}  # Already taken for periods 1, 3
        )
        room_avail = Availability({'mon': [10, 11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        teacher = Teacher(8, "Prof. Red", 40, teacher_avail)
        room = Room(108, 50, room_avail, [])
        group = Group(11, 1, 1, 30, Availability({'mon': [10, 11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}), [], [8], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        # Try to reserve with overlapping mask
        record = Record(11, [8], [108], 'mon', 10, [1, 2])
        result = problem.add_record_and_update_availability(record)
        
        # Should fail because period 1 is already taken
        self.assertFalse(result)
        self.assertNotIn(record, problem.records)