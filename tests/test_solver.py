from src import ALGORITHMS_AVAILABLE, Problem, Availability, Teacher, Room, Group, Solver, Response, Allocation
import unittest

class TestSolver(unittest.TestCase):
    def test_solve_simple_case(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Setup a simple problem with one group, one teacher, one room
                problem = Problem()
                
                teacher_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                
                teacher = Teacher(1, teacher_avail)
                room = Room(101, 50, room_avail, ["lab"])
                group = Group(1, 1, 30, group_avail, [[["lab"]]], [1], [])
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed and return a Response with status 0
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                self.assertIn(result.solution[0].day, [1])
                self.assertIn(result.solution[0].slot, [10, 11, 12])
                self.assertEqual(result.solution[0].room_ids, [101])

    def test_solve_when_group_has_no_teacher(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Setup a simple problem with one group, one teacher, one room
                problem = Problem()
                
                room_avail = Availability({1: [10, 11, 12]})
                group_avail = Availability({1: [10, 11, 12]})
                
                room = Room(101, 50, room_avail, ["lab"])
                group = Group(1, 1, 30, group_avail, [[["lab"]]], [], [])
                
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed and return a Response with status 0
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                self.assertIn(result.solution[0].day, [1])
                self.assertIn(result.solution[0].slot, [10, 11, 12])
                self.assertEqual(result.solution[0].room_ids, [101])

    def test_solve_multiple_groups(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Setup with multiple groups
                problem = Problem()
                
                teacher1_avail = Availability({1: [10, 11, 12, 13]})
                teacher2_avail = Availability({1: [10, 11, 12, 13]})
                room1_avail = Availability({1: [10, 11, 12, 13]})
                room2_avail = Availability({1: [10, 11, 12, 13]})
                group1_avail = Availability({1: [10, 11, 12, 13]})
                group2_avail = Availability({1: [10, 11, 12, 13]})
                
                teacher1 = Teacher(1, teacher1_avail)
                teacher2 = Teacher(2, teacher2_avail)
                room1 = Room(101, 50, room1_avail, ["lab"])
                room2 = Room(102, 50, room2_avail, ["lab"])
                group1 = Group(1, 1, 30, group1_avail, [[["lab"]]], [1], [])
                group2 = Group(2, 1, 30, group2_avail, [[["lab"]]], [2], [])
                
                problem.add_teacher(teacher1)
                problem.add_teacher(teacher2)
                problem.add_room(room1)
                problem.add_room(room2)
                problem.add_group(group1)
                problem.add_group(group2)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed and return allocations for both groups
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 2)
                group_ids = [r.group_id for r in result.solution]
                self.assertIn(1, group_ids)
                self.assertIn(2, group_ids)

    def test_solve_no_solution(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Setup an impossible problem (teacher not available when group is)
                problem = Problem()
                
                teacher_avail = Availability({1: [10], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room_avail = Availability({1: [11], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group_avail = Availability({1: [11], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                
                teacher = Teacher(1, teacher_avail)
                room = Room(101, 50, room_avail, ["lab"])
                group = Group(1, 1, 30, group_avail, [[["lab"]]], [1], [])
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should fail and return Response with status 1
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 1)
                self.assertEqual(len(result.solution), 0)

    def test_solve_with_established_allocations(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Setup with one group already scheduled
                problem = Problem()
                
                teacher1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                teacher2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                
                teacher1 = Teacher(1, teacher1_avail)
                teacher2 = Teacher(2, teacher2_avail)
                room1 = Room(101, 50, room1_avail, ["lab"])
                room2 = Room(102, 50, room2_avail, ["lab"])
                group1 = Group(1, 1, 30, group1_avail, [[["lab"]]], [1], [])
                group2 = Group(2, 1, 30, group2_avail, [[["lab"]]], [2], [])
                
                problem.add_teacher(teacher1)
                problem.add_teacher(teacher2)
                problem.add_room(room1)
                problem.add_room(room2)
                problem.add_group(group1)
                problem.add_group(group2)
                
                # Add an established allocation for group 1
                problem.add_allocation(Allocation(1, [101], 1, 10))
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed and return allocations for both groups (including the established one)
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 2)
                
                # The first allocations should be the established one
                self.assertEqual(result.solution[0].group_id, 1)
                self.assertEqual(result.solution[0].day, 1)
                self.assertEqual(result.solution[0].slot, 10)
                
                # The second should be the newly solved group 2
                self.assertEqual(result.solution[1].group_id, 2)

    def test_solve_with_duration_greater_than_one(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Test with a group that requires 2 slots
                problem = Problem()
                
                teacher_avail = Availability({1: [10, 11, 12, 13], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room_avail = Availability({1: [10, 11, 12, 13], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group_avail = Availability({1: [10, 11, 12, 13], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                
                teacher = Teacher(1, teacher_avail)
                room = Room(101, 50, room_avail, ["lab"])
                group = Group(1, 2, 30, group_avail, [[["lab"]]], [1], [])
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                
                # Verify the slot and the next slot are both available in group's availability
                start_slot = result.solution[0].slot
                self.assertIn(start_slot, group_avail.slots[result.solution[0].day])
                self.assertIn(start_slot + 1, group_avail.slots[result.solution[0].day])

    def test_solve_with_period_mask(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Test with groups that have period masks
                problem = Problem()
                
                teacher_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                
                teacher = Teacher(1, teacher_avail)
                room = Room(101, 50, room_avail, ["lab"])
                group = Group(1, 1, 30, group_avail, [[["lab"]]], [1], [1, 3])  # period_mask = [1, 3]
                
                problem.add_teacher(teacher)
                problem.add_room(room)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)

    def test_solve_multiple_teachers_multiple_rooms(self):
        for method in ALGORITHMS_AVAILABLE:
            with self.subTest(f"SOLVE USING OPTION {method}"):
                # Test with a group requiring multiple teachers and multiple rooms (via labels)
                problem = Problem()
                
                teacher1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                teacher2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                room2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                group_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
                
                teacher1 = Teacher(1, teacher1_avail)
                teacher2 = Teacher(2, teacher2_avail)
                room1 = Room(101, 30, room1_avail, ["LAB"])
                room2 = Room(102, 30, room2_avail, ["PROJECTOR"])
                # Group needs 2 teachers and 2 different room types (LAB and PROJECTOR)
                group = Group(1, 1, 25, group_avail, [[["LAB"]], [["PROJECTOR"]]], [1, 2], [])
                
                problem.add_teacher(teacher1)
                problem.add_teacher(teacher2)
                problem.add_room(room1)
                problem.add_room(room2)
                problem.add_group(group)
                
                solver = Solver()
                result = solver.solve(problem, method)
                
                # Should succeed
                self.assertIsInstance(result, Response)
                self.assertEqual(result.status, 0)
                self.assertEqual(len(result.solution), 1)
                self.assertEqual(result.solution[0].group_id, 1)
                # Should have 2 rooms (one for each label set)
                self.assertEqual(len(result.solution[0].room_ids), 2)
