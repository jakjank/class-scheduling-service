import unittest
from backend.src import *

SOLVER_OPTIONS = [0, 1, 2]

class TestSolver(unittest.TestCase):
    def test_solve_simple_case(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Setup a simple problem with one group, one teacher, one room
                problem = Problem()
                
                teacher_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher = Teacher(1, "Prof. A", 40, teacher_avail)
                room = Room(101, 50, room_avail, [])
                group = Group(1, 1, 1, 30, group_avail, [], [1], [])
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should succeed and return a Response with status 0
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                self.assertIn(result.solution[0].day, ['mon'])
                self.assertIn(result.solution[0].hour, [10, 11, 12])
                self.assertEqual(result.solution[0].teachers_ids, [1])
                self.assertEqual(result.solution[0].rooms_ids, [101])

    def test_solve_multiple_groups(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Setup with multiple groups
                problem = Problem()
                
                teacher1_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                teacher2_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room1_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room2_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group1_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group2_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher1 = Teacher(1, "Prof. A", 40, teacher1_avail)
                teacher2 = Teacher(2, "Prof. B", 40, teacher2_avail)
                room1 = Room(101, 50, room1_avail, [])
                room2 = Room(102, 50, room2_avail, [])
                group1 = Group(1, 1, 1, 30, group1_avail, [], [1], [])
                group2 = Group(2, 1, 1, 30, group2_avail, [], [2], [])
                
                problem.add_teacher(teacher1)
                problem.add_teacher(teacher2)
                problem.add_room(room1)
                problem.add_room(room2)
                problem.add_group(group1)
                problem.add_group(group2)
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should succeed and return records for both groups
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 2)
                group_ids = [r.group_id for r in result.solution]
                self.assertIn(1, group_ids)
                self.assertIn(2, group_ids)

    def test_solve_no_solution(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Setup an impossible problem (teacher not available when group is)
                problem = Problem()
                
                teacher_avail = Availability({'mon': [10], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room_avail = Availability({'mon': [11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group_avail = Availability({'mon': [11], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher = Teacher(1, "Prof. A", 40, teacher_avail)
                room = Room(101, 50, room_avail, [])
                group = Group(1, 1, 1, 30, group_avail, [], [1], [])
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should fail and return Response with status 1
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 1)
                self.assertEqual(len(result.solution), 0)

    def test_solve_with_established_records(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Setup with one group already scheduled
                problem = Problem()
                
                teacher1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                teacher2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher1 = Teacher(1, "Prof. A", 40, teacher1_avail)
                teacher2 = Teacher(2, "Prof. B", 40, teacher2_avail)
                room1 = Room(101, 50, room1_avail, [])
                room2 = Room(102, 50, room2_avail, [])
                group1 = Group(1, 1, 1, 30, group1_avail, [], [1], [])
                group2 = Group(2, 1, 1, 30, group2_avail, [], [2], [])
                
                problem.add_teacher(teacher1)
                problem.add_teacher(teacher2)
                problem.add_room(room1)
                problem.add_room(room2)
                problem.add_group(group1)
                problem.add_group(group2)
                
                # Add an established record for group 1
                problem.add_record(Record(1, [1], [101], 'mon', 10, []))
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should succeed and return records for both groups (including the established one)
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 2)
                
                # The first record should be the established one
                self.assertEqual(result.solution[0].group_id, 1)
                self.assertEqual(result.solution[0].day, 'mon')
                self.assertEqual(result.solution[0].hour, 10)
                
                # The second should be the newly solved group 2
                self.assertEqual(result.solution[1].group_id, 2)

    def test_solve_with_duration_greater_than_one(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Test with a group that requires 2 hours
                problem = Problem()
                
                teacher_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group_avail = Availability({'mon': [10, 11, 12, 13], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher = Teacher(1, "Prof. A", 40, teacher_avail)
                room = Room(101, 50, room_avail, [])
                group = Group(1, 1, 2, 30, group_avail, [], [1], [])  # duration = 2
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should succeed
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                
                # Verify the hour and the next hour are both available in group's availability
                start_hour = result.solution[0].hour
                self.assertIn(start_hour, group_avail.hours[result.solution[0].day])
                self.assertIn(start_hour + 1, group_avail.hours[result.solution[0].day])

    def test_solve_with_period_mask(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Test with groups that have period masks
                problem = Problem()
                
                teacher_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher = Teacher(1, "Prof. A", 40, teacher_avail)
                room = Room(101, 50, room_avail, [])
                group = Group(1, 1, 1, 30, group_avail, [], [1], [1, 3])  # period_mask = [1, 3]
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should succeed
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                self.assertEqual(result.solution[0].period_mask, [1, 3])

    def test_solve_multiple_teachers_multiple_rooms(self):
        for option in SOLVER_OPTIONS:
            with self.subTest(f"SOLVE USING OPTION {option}"):
                # Test with a group requiring multiple teachers and multiple rooms (via labels)
                problem = Problem()
                
                teacher1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                teacher2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room1_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                room2_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                group_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
                
                teacher1 = Teacher(1, "Prof. A", 40, teacher1_avail)
                teacher2 = Teacher(2, "Prof. B", 40, teacher2_avail)
                room1 = Room(101, 30, room1_avail, ["LAB"])
                room2 = Room(102, 30, room2_avail, ["PROJECTOR"])
                # Group needs 2 teachers and 2 different room types (LAB and PROJECTOR)
                group = Group(1, 1, 1, 25, group_avail, [["LAB"], ["PROJECTOR"]], [1, 2], [])
                
                problem.add_teacher(teacher1)
                problem.add_teacher(teacher2)
                problem.add_room(room1)
                problem.add_room(room2)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, option)
                
                # Should succeed
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                # Should have 2 teachers
                self.assertEqual(len(result.solution[0].teachers_ids), 2)
                self.assertIn(1, result.solution[0].teachers_ids)
                self.assertIn(2, result.solution[0].teachers_ids)
                # Should have 2 rooms (one for each label set)
                self.assertEqual(len(result.solution[0].rooms_ids), 2)
