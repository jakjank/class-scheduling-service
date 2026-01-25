from src import covers, check_occurrence_desc, is_cluster_satisfied, get_all_placements_for_group
from src import Problem, Group, Teacher, Availability, Room, Cluster, Allocation
import unittest

class TestUtils(unittest.TestCase):

    def test_covers(self):
        self.assertFalse(covers([10,11,12,13], 9, 2))
        self.assertFalse(covers([10,11,12,13], 13, 2))
        self.assertTrue(covers([10,11,12,13], 10, 2))
        self.assertTrue(covers([10,11,12,13], 12, 2))

    def test_check_occurrence_desc(self):
        self.assertFalse(check_occurrence_desc([1,2,3,4],[3]))
        self.assertFalse(check_occurrence_desc([],[3]))
        self.assertTrue(check_occurrence_desc([1,2,3,4],[]))
        self.assertTrue(check_occurrence_desc([1,3],[2,4]))

    def test_is_cluster_satisfied(self):
        day_slot_duration = [(1, 10, 2), (1, 12, 2), (2, 10, 2)]
        self.assertFalse(is_cluster_satisfied([2], day_slot_duration))
        self.assertFalse(is_cluster_satisfied([1], day_slot_duration))
        self.assertFalse(is_cluster_satisfied([1], [(1, 10, 2)]))
        self.assertFalse(is_cluster_satisfied([4], day_slot_duration))
        self.assertFalse(is_cluster_satisfied([2,2], day_slot_duration))
        self.assertFalse(is_cluster_satisfied([4], [(1, 10, 2),(1, 13, 2)]))

        self.assertTrue(is_cluster_satisfied([2,4],day_slot_duration))
        self.assertTrue(is_cluster_satisfied([2,2,2], day_slot_duration))
        self.assertTrue(is_cluster_satisfied([3], [(1, 10, 2)]))
        self.assertTrue(is_cluster_satisfied([2,2,2], [(1, 10, 2),(1, 14, 2), (2, 10, 2)]))
        self.assertTrue(is_cluster_satisfied([5], [(1, 10, 2),(1, 13, 2)]))
        self.assertTrue(is_cluster_satisfied([2,2,2], [(1, 10, 2),(1, 13, 2)]))

        self.assertTrue(is_cluster_satisfied([2,4], [(1,10,2),(4,10,2),(4,11,2)]))

    def test_is_cluster_satisfied_works_well_with_empty_range(self):
        day_slot_duration_1 = [(1, 10, 2), (1, 12, 2)]
        day_slot_duration_2 = [(1, 10, 2), (1, 11, 2)]
        self.assertTrue(is_cluster_satisfied([], day_slot_duration_1))
        self.assertFalse(is_cluster_satisfied([], day_slot_duration_2))

    def test_getAllPlacementsForGroup_should_check_group_avail(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,12,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3,34,Availability({1:[10,11,12,13,14,15]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return since group own Availibility does not cover its duration
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_teacher_avail(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,12,14]})))
        problem.add_room(Room(3,34,Availability({1:[10,11,12,13,14]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since teacher does not own Availibility covering group duration
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_room_avail(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [[["lab"]]], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3,34,Availability({1:[10,12,14]}), ["lab"]))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since no room owns Availibility covering group duration
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_room_capacity(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [[["lab"]]], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 28, Availability({1:[10,11,12,13,14]}), ["lab"]))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since no room has capacity covering group capacity
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_room_labels(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [[["TV"]]], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({1:[10,11,12,13,14]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since no room has "TV" label
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_teacher_occurrence_desc(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [[["TV"]]], [2], [1,3])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]}), [3]))
        problem.add_room(Room(3, 34, Availability({1:[10,11,12,13,14]}), ["TV"]))

        # Should return [] since teacher taken periods collide with group needed period mask
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_teacher_occurrence_desc(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [[["TV"]]], [2], [1,3])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({1:[10,11,12,13,14,15]}, {(1, 10) : [1,4],
                                                                                (1, 11) : [1,4],
                                                                                (1, 12) : [1,4],
                                                                                (1, 13) : [1,4],
                                                                                (1, 14) : [1,4]}), ["TV"]))

        # Should return [] since all rooms taken periods collide with group needed period mask
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_manage_group_with_no_teacher(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [[["TV"]]], [], [1,3])
        problem.add_group(group)
        problem.add_room(Room(3,
                              34,
                              Availability(
                                  {1:[10,11,12,13,14,15]},
                                  {
                                   (1, 10) : [2,4],
                                   (1, 11) : [2,4],
                                   (1, 12) : [2,4],
                                   (1, 13) : [2,4],
                                   (1, 14) : [2,4]}
                               ),
                               ["TV"]
                               )
                        )

        # Should return find all placements
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(len(placements), 4)

    def test_getAllPlacementsForGroup_should_manage_group_with_no_room(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))

        # Should return all possible placements
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(len(placements), 4)

    def test_getAllPlacementsForGroup_should_manage_group_with_no_room_and_no_teacher(self):
        problem = Problem()
        group = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [], [], [])
        problem.add_group(group)

        # Should return all possible placements
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(len(placements), 4)

    def test_getAllPlacementsForGroup_should_check_clustering(self):
        problem = Problem()
        g1 = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [], [2], [])
        g2 = Group(2,2,30,Availability({1:[12,13,14]}), [], [3], [])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))
        problem.add_teacher(Teacher(3, Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({1:[10,11,12,13,14]}), []))
        problem.add_cluster(Cluster([2], [1,2]))
        problem.add_allocation(Allocation(1, [3], 1, 10))

        # Should return [] since it possible to place g2 but not in the same 'cluster' where g1 is
        placements = get_all_placements_for_group(g2, problem)
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_use_few_cluster_blocks_if_needed(self):
        problem = Problem()
        g1 = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [], [2], [])
        g2 = Group(2,2,30,Availability({2:[12,13,14]}), [], [2], [])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15], 2:[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({1:[10,11,12,13,14], 2:[10,11,12,13,14,15]}), []))
        problem.add_cluster(Cluster([2,2], [1,2]))
        problem.add_allocation(Allocation(1, [3], 1, 10))

        # Should find placements since 2 blocks in cluster are available
        # (one class is assigned at monday and other one has availability only on tuesday)
        placements = get_all_placements_for_group(g2, problem)
        self.assertEqual(len(placements), 2)

    def test_getAllPlacementsForGroup_should_use_few_cluster_blocks_for_one_day_if_needed(self):
        problem = Problem()
        g1 = Group(1,2,30,Availability({1:[10,11]}), [], [2], [])
        g2 = Group(2,2,30,Availability({1:[14,15]}), [], [2], [])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({1:[10,11,12,13,14,15]}), []))
        problem.add_cluster(Cluster([2,2], [1,2]))
        problem.add_allocation(Allocation(1, [2], 1, 10))

        # Should  find placement for g2 since it possible to 2 two h-long blocks on one day are satysfying the cluster
        placements = get_all_placements_for_group(g2, problem)
        self.assertEqual(len(placements), 1)

    def test_getAllPlacementsForGroup_should_find_all_placements(self):
        problem = Problem()
        g1 = Group(1,2,30,Availability({1:[10,11,12,13,14]}), [], [2], [1,3])
        g2 = Group(2,2,30,Availability({1:[12,13,14,15]}), [], [2], [1,3])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2, Availability({1:[10,11,12,13,14,15]}, {(1, 10) : [2,4],
                                                                                                      (1, 11) : [2,4],
                                                                                                      (1, 12) : [2,4],
                                                                                                      (1, 13) : [2,4],
                                                                                                      (1, 14) : [2,4]})))
        problem.add_room(Room(3, 30, Availability({1:[10,11,12,13,14]}), []))
        problem.add_cluster(Cluster([5], [1,2]))
        problem.add_allocation(Allocation(1, [3], 1, 10))

        placements = get_all_placements_for_group(g2, problem)
        # Should find all placements (1 12 and 13, not at 1 14 because cluster range is 5h long)
        self.assertEqual(len(placements), 2)
