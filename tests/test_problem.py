from src import Problem, Group, Availability, Allocation, Teacher, Room, Cluster
import unittest

class TestProblem(unittest.TestCase):
    def test_check_group_presence(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [], [15], []))
        response = problem.check()

        self.assertEqual(response[0].msg, "Group with id=17 is not present in solution")

    def test_check_teacher_availability(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({4 : [15, 16]}), [], [15], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_allocation(Allocation(17, [5], 4, [15,16]))
        response = problem.check()

        self.assertEqual(response[0].msg, "Teacher with id=15 is not available on 4 in each slot out of [15, 16]")

    def test_check_teacher_conflicts(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 2, 30, Availability({}), [], [15], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_allocation(Allocation(17,[5], 5, [10,11]))
        problem.add_allocation(Allocation(18,[6], 5, [11,12]))
        response = problem.check()

        self.assertIn(response[0].msg, "Teacher with id=15 has conflicting classes on 5 between 10 and 13")
    
    def test_check_room_availability(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [], [15], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_allocation(Allocation(17,[5], 5, [10,11]))
        problem.add_room(Room(5, 36, Availability({4 : [8,9]}), []))
        response = problem.check()

        self.assertEqual(response[0].msg, "Room with id=5 is not available on 5 in slots [10, 11]")

    def test_check_room_colission(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [], [15], []))
        problem.add_group(Group(18, 2, 30, Availability({5 : [10,11]}), [], [16], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_teacher(Teacher(16, Availability({5 : [10,11]})))
        problem.add_room(Room(5, 36, Availability({5 : [8,9,10,11,12]}), []))
        problem.add_allocation(Allocation(17,[5], 5, [10,11]))
        problem.add_allocation(Allocation(18,[5], 5, [11,12]))
        response = problem.check()

        self.assertEqual(response[0].msg, "At least two groups (id=17, id=18) use room with id=5 at the same time on 5 in slots [10, 11]")

    def test_check_room_labels(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [[["TV", "LAB"]]], [15], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_room(Room(5, 36, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_allocation(Allocation(17,[5], 5, [10,11]))
        response = problem.check()

        self.assertEqual(response[0].msg, "Group with id=17 has room(s) with labels=[['LAB']] but needs labels=[[['TV', 'LAB']]]")

    def test_check_room_capacity(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [15], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_room(Room(5, 24, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_allocation(Allocation(17, [5], 5, [10,11]))
        response = problem.check()

        self.assertEqual(response[0].msg, "Group with id=17 has capacity=30 but has assigned room (id=5) with capacity=24")

    def test_check_cluster_satisfaction_slots(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [15], []))
        problem.add_group(Group(18, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [16], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_teacher(Teacher(16, Availability({5 : [10,11]})))
        problem.add_room(Room(5, 36, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_room(Room(6, 36, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_cluster(Cluster(1, [2], [17,18]))
        problem.add_allocation(Allocation(17, [5], 5, [10,11]))
        problem.add_allocation(Allocation(18, [6], 5, [12,13]))
        response = problem.check()

        self.assertEqual(response[0].msg, "Cluster connecting groups with ids 17, 18 is not satisfied")

    def test_check_cluster_satisfaction_daily(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [15], []))
        problem.add_group(Group(18, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [16], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_teacher(Teacher(16, Availability({5 : [10,11]})))
        problem.add_room(Room(5, 36, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_room(Room(6, 36, Availability({4 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_cluster(Cluster(1, [2], [17,18]))
        problem.add_allocation(Allocation(17, [5], 5, [10,11]))
        problem.add_allocation(Allocation(18, [6], 4, [10,11]))
        response = problem.check()

        self.assertEqual(response[0].msg, "Cluster connecting groups with ids 17, 18 is not satisfied")

    def test_check_cluster_satisfaction_complicated(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [15], []))
        problem.add_group(Group(18, 2, 30, Availability({5 : [10,11,12,13], 4 : [10,11]}), [[["LAB"]]], [16], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_teacher(Teacher(16, Availability({5 : [10,11,12,13], 4 : [10,11]})))
        problem.add_room(Room(5, 36, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_room(Room(6, 36, Availability({4 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_cluster(Cluster(1, [2,2], [17,18]))
        problem.add_allocation(Allocation(17, [5], 5, [10,11]))
        problem.add_allocation(Allocation(18, [6], 4, [10,11]))
        response = problem.check()

        self.assertEqual(response, [])

    def test_check_cluster_satisfaction_complicated2(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({5 : [10,11]}), [[["LAB"]]], [15], []))
        problem.add_group(Group(18, 2, 30, Availability({5 : [10,11,12,13]}), [[["LAB"]]], [16], []))
        problem.add_teacher(Teacher(15, Availability({5 : [10,11]})))
        problem.add_teacher(Teacher(16, Availability({5 : [10,11,12,13]})))
        problem.add_room(Room(5, 36, Availability({5 : [8,9,10,11,12]}), ["LAB"]))
        problem.add_room(Room(6, 36, Availability({5 : [8,9,10,11,12,13]}), ["LAB"]))
        problem.add_cluster(Cluster(1, [2,2], [17,18]))
        problem.add_allocation(Allocation(17, [5], 5, [10,11]))
        problem.add_allocation(Allocation(18, [6], 5, [12,13]))
        response = problem.check()

        self.assertEqual(response, [])
    
    def test_check_group_availability(self):
        problem = Problem()
        problem.add_group(Group(17, 2, 30, Availability({4 : [15, 16]}), [], [], []))
        problem.add_allocation(Allocation(17, [], 4, [16,17]))
        response = problem.check()

        self.assertEqual(response[0].msg, "Group with id=17 cannot take place on 4 in slots [16, 17]")

    def test_add_allocation_and_update_availability_single_slot_no_mask(self):
        problem = Problem()
        teacher_avail = Availability({1: [10, 11, 12]})
        room_avail = Availability({1: [10, 11, 12]})
        
        teacher = Teacher(1, teacher_avail)
        room = Room(101, 50, room_avail, ["LAB"])
        group = Group(5, 1, 30, Availability({1: [10, 11, 12]}), [[["LAB"]]], [1], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        alloc = Allocation(5, [101], 1, [10])
        result = problem.add_allocation_and_update_availability(alloc)
        
        self.assertTrue(result)
        self.assertEqual(teacher.availability.slots[1], [11, 12])
        self.assertEqual(room.availability.slots[1], [11, 12])
        self.assertIn(alloc, problem.allocations)

    def test_add_allocation_and_update_availability_multi_slot_no_mask(self):
        problem = Problem()
        teacher_avail = Availability({1: [10, 11, 12, 13]})
        room_avail = Availability({1: [10, 11, 12, 13]})
        
        teacher = Teacher(2, teacher_avail)
        room = Room(102, 30, room_avail, ["LAB"])
        group = Group(6, 3, 25, Availability({1: [10, 11, 12, 13]}), [[["LAB"]]], [2], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        alloc = Allocation(6, [102], 1, [10,11,12])
        result = problem.add_allocation_and_update_availability(alloc)
        
        self.assertTrue(result)
        # Should remove slots 10, 11, 12 (3 slot duration)
        self.assertEqual(teacher.availability.slots[1], [13])
        self.assertEqual(room.availability.slots[1], [13])
        self.assertIn(alloc, problem.allocations)

    def test_add_allocation_and_update_availability_with_mask(self):
        problem = Problem()
        teacher_avail = Availability({1: [10, 11, 12]})
        room_avail = Availability({1: [10, 11, 12]})
        
        teacher = Teacher(3, teacher_avail)
        room = Room(103, 40, room_avail, ["LAB"])
        group = Group(7, 2, 35, Availability({1: [10, 11, 12]}), [[["LAB"]]], [3], [1, 3])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        alloc = Allocation(7, [103], 1, [10,11])
        result = problem.add_allocation_and_update_availability(alloc)
        
        self.assertTrue(result)
        # slots should still exist but have taken_periods
        self.assertEqual(teacher.availability.slots[1], [10, 11, 12])
        self.assertEqual(room.availability.slots[1], [10, 11, 12])
        self.assertEqual(teacher.availability.taken_periods[(1, 10)], [1, 3])
        self.assertEqual(teacher.availability.taken_periods[(1, 11)], [1, 3])
        self.assertEqual(room.availability.taken_periods[(1, 10)], [1, 3])
        self.assertEqual(room.availability.taken_periods[(1, 11)], [1, 3])
        self.assertIn(alloc, problem.allocations)

    def test_add_allocation_and_update_availability_teacher_unavailable(self):
        problem = Problem()
        teacher_avail = Availability({1: [10, 11]})
        room_avail = Availability({1: [10, 11, 12]})
        
        teacher = Teacher(4, teacher_avail)
        room = Room(104, 50, room_avail, ["LAB"])
        group = Group(8, 2, 30, Availability({1: [10, 11, 12]}), [[["LAB"]]], [4], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        # Teacher only available for slots 10-11, but class needs slots 11-12
        alloc = Allocation(8, [104], 1, [11,12])
        result = problem.add_allocation_and_update_availability(alloc)
        
        # Should fail because slot 12 is not available for teacher
        self.assertFalse(result)
        self.assertNotIn(alloc, problem.allocations)

    def test_add_alloc_and_update_availability_room_unavailable(self):
        problem = Problem()
        teacher_avail = Availability({1: [10, 11, 12]})
        room_avail = Availability({1: [10, 11], 2: []})
        
        teacher = Teacher(5, teacher_avail)
        room = Room(105, 50, room_avail, ["LAB"])
        group = Group(9, 2, 30, Availability({1: [10, 11, 12]}), [[["LAB"]]], [5], [])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        # Room only available for slots 10-11, but class needs slots 11-12 (2 slots starting at 11)
        alloc = Allocation(9, [105], 1, [11,12])
        result = problem.add_allocation_and_update_availability(alloc)
        
        # Should fail because slot 12 is not available for room
        self.assertFalse(result)
        self.assertNotIn(alloc, problem.allocations)

    def test_add_allocation_and_update_availability_multiple_teachers_and_rooms(self):
        problem = Problem()
        teacher1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        teacher2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        room1_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        room2_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        
        teacher1 = Teacher(6, teacher1_avail)
        teacher2 = Teacher(7, teacher2_avail)
        room1 = Room(106, 30, room1_avail, ["LAB"])
        room2 = Room(107, 30, room2_avail, ["CLASS"])
        group = Group(10, 2, 50, Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}), [[["LAB"]],[["CLASS"]]], [6, 7], [])
        
        problem.add_teacher(teacher1)
        problem.add_teacher(teacher2)
        problem.add_room(room1)
        problem.add_room(room2)
        problem.add_group(group)
        
        alloc = Allocation(10, [106, 107], 1, [10,11])
        result = problem.add_allocation_and_update_availability(alloc)
        
        self.assertTrue(result)
        # Both teachers should have slots 10, 11 removed
        self.assertEqual(teacher1.availability.slots[1], [12])
        self.assertEqual(teacher2.availability.slots[1], [12])
        # Both rooms should have slots 10, 11 removed
        self.assertEqual(room1.availability.slots[1], [12])
        self.assertEqual(room2.availability.slots[1], [12])
        self.assertIn(alloc, problem.allocations)

    def test_add_allocation_and_update_availability_conflicting_mask(self):
        problem = Problem()
        teacher_avail = Availability(
            {1: [10, 11]},
            {(1, 10): [1, 3]}  # Already taken for periods 1, 3
        )
        room_avail = Availability({1: [10, 11], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        
        teacher = Teacher(8, teacher_avail)
        room = Room(108, 50, room_avail, ["LAB"])
        group = Group(11, 1, 30, Availability({1: [10, 11]}), [[["LAB"]]], [8], [1,2])
        
        problem.add_teacher(teacher)
        problem.add_room(room)
        problem.add_group(group)
        
        # Try to reserve with overlapping mask
        alloc = Allocation(11, [108], 1, [10])
        result = problem.add_allocation_and_update_availability(alloc)
        
        # Should fail because period 1 is already taken
        self.assertFalse(result)
        self.assertNotIn(alloc, problem.allocations)

    def test_adding_teachers_with_same_id_should_trow(self):
        problem = Problem()
        t1 = Teacher(42, Availability({}))
        t2 = Teacher(42, Availability({}))

        problem.add_teacher(t1)

        with self.assertRaises(ValueError) as err:
            problem.add_teacher(t2)

        self.assertIn("Teachers should have unique ids. Id '42' repeats.", str(err.exception))

    def test_adding_groups_with_same_id_should_trow(self):
        problem = Problem()
        g1 = Group(9, 2, 30, Availability({}), [], [], [])
        g2 = Group(9, 2, 24, Availability({}), [], [], [])
        
        problem.add_group(g1)

        with self.assertRaises(ValueError) as err:
            problem.add_group(g2)

        self.assertIn("Groups should have unique ids. Id '9' repeats.", str(err.exception))

    def test_adding_rooms_with_same_id_should_trow(self):
        problem = Problem()
        r1 = Room(8, 30, Availability({}), ["pracownia"])
        r2 = Room(8, 24, Availability({}), ["cwiczenia"])
        
        problem.add_room(r1)

        with self.assertRaises(ValueError) as err:
            problem.add_room(r2)

        self.assertIn("Rooms should have unique ids. Id '8' repeats.", str(err.exception))

    def test_add_alloc_after_cluster_should_add_alloc_to_cluster(self):
        prob = Problem()

        prob.add_cluster(Cluster(1, [2,2],[31,32]))
        prob.add_allocation(Allocation(31, [], 1, [8,9]))

        self.assertEqual(prob.clusters[0].allocations[0].group_id, 31)
        self.assertEqual(len(prob.clusters[0].allocations), 1)

    def test_add_cluster_after_alloc_should_add_alloc_to_cluster(self):
        prob = Problem()

        prob.add_allocation(Allocation(31, [], 1, [8,9]))
        prob.add_cluster(Cluster(1, [2,2],[31,32]))

        self.assertEqual(prob.clusters[0].allocations[0].group_id, 31)
        self.assertEqual(len(prob.clusters[0].allocations), 1)

    def test_adding_clusters_with_same_id_should_trow(self):
        problem = Problem()
        c1 = Cluster(8, [], [1,2])
        c2 = Cluster(8, [2], [3,4])
        
        problem.add_room(c1)

        with self.assertRaises(ValueError) as err:
            problem.add_room(c2)

        self.assertIn("Rooms should have unique ids. Id '8' repeats.", str(err.exception))

    def test_full_check_should_return_all_problems(self):
        p = Problem()

        g1 = Group(1,2,30,Availability({1:[8,9,10,11]}), [], [1], [])
        g2 = Group(2,2,30,Availability({1:[8,9,10,11]}), [], [1], [])
        t = Teacher(1,Availability({}))
        c = Cluster(1, [], [1, 2])
        a1 = Allocation(1, [], 2, [8,9])
        a2 = Allocation(2, [], 2, [8,9])

        p.add_group(g1)
        p.add_group(g2)
        p.add_teacher(t)
        p.add_cluster(c)
        p.add_allocation(a1)
        p.add_allocation(a2)

        # Problems:
        # 1: g1 is not available on tuesday
        # 2: g2 is not available on tuesday
        # 3: g1's teacher is not available on tuesday
        # 4: g2's teacher is not available on tuesday
        # 5: g1 and g2 cannot overlap (x - first g1 checks it overlaps g2 but should not and g2 checks the same)
        # 6: teacher has conflicting classes (x2 - as above)

        failed_constraints = p.check(method="full_check")
        self.assertEqual(len(failed_constraints), 8)
