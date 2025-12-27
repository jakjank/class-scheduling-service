import unittest
from backend.src.utils import *

class TestUtils(unittest.TestCase):

    def test_covers(self):
        self.assertFalse(covers([10,11,12,13], 9, 2))
        self.assertFalse(covers([10,11,12,13], 13, 2))
        self.assertTrue(covers([10,11,12,13], 10, 2))
        self.assertTrue(covers([10,11,12,13], 12, 2))

    def test_check_period_mask(self):
        self.assertFalse(check_period_mask([1,2,3,4],[3]))
        self.assertFalse(check_period_mask([],[3]))
        self.assertTrue(check_period_mask([1,2,3,4],[]))
        self.assertTrue(check_period_mask([1,3],[2,4]))

    def test_is_cluster_satified(self):
        day_hour_duration = [("mon", 10, 2),("mon", 12, 2), ("tue", 10, 2)]
        self.assertFalse(is_cluster_satisfied([2], day_hour_duration))
        self.assertFalse(is_cluster_satisfied([1], day_hour_duration))
        self.assertFalse(is_cluster_satisfied([1], [("mon", 10, 2)]))
        self.assertFalse(is_cluster_satisfied([4], day_hour_duration))
        self.assertFalse(is_cluster_satisfied([2,2], day_hour_duration))
        self.assertFalse(is_cluster_satisfied([4], [("mon", 10, 2),("mon", 13, 2)]))

        self.assertTrue(is_cluster_satisfied([2,4],day_hour_duration))
        self.assertTrue(is_cluster_satisfied([2,2,2], day_hour_duration))
        self.assertTrue(is_cluster_satisfied([3], [("mon", 10, 2)]))
        self.assertTrue(is_cluster_satisfied([2,2,2], [("mon", 10, 2),("mon", 14, 2), ("tue", 10, 2)]))
        self.assertTrue(is_cluster_satisfied([5], [("mon", 10, 2),("mon", 13, 2)]))
        self.assertTrue(is_cluster_satisfied([2,2,2], [("mon", 10, 2),("mon", 13, 2)]))

    def test_getAllPlacementsForGroup_should_check_group_avail(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,12,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3,34,Availability({"mon":[10,11,12,13,14,15]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return since group own Availibility does not cover its duration
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_teacher_avail(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,12,14]})))
        problem.add_room(Room(3,34,Availability({"mon":[10,11,12,13,14]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since teacher does not own Availibility covering group duration
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_room_avail(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3,34,Availability({"mon":[10,12,14]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since no room owns Availibility covering group duration
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_room_capacity(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), [], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 28, Availability({"mon":[10,11,12,13,14]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since no room has capacity covering group capacity
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_room_labels(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), ["TV"], [2], [])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({"mon":[10,11,12,13,14]}), []))

        placements = get_all_placements_for_group(group, problem)
        # Should return [] since no room has "TV" label
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_teacher_period_mask(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), ["TV"], [2], [1,3])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]}), [3]))
        problem.add_room(Room(3, 34, Availability({"mon":[10,11,12,13,14]}), []))

        # Should return [] since teacher taken periods collide with group needed period mask
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_teacher_period_mask(self):
        problem = Problem()
        group = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), ["TV"], [2], [1,3])
        problem.add_group(group)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({"mon":[10,11,12,13,14,15]}, {("mon", 10) : [2,4],
                                                                                ("mon", 11) : [2,4],
                                                                                ("mon", 12) : [2,4],
                                                                                ("mon", 13) : [2,4],
                                                                                ("mon", 14) : [2,4]}), []))

        # Should return [] since all rooms taken periods collide with group needed period mask
        placements = get_all_placements_for_group(group, problem)
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_check_clustering(self):
        problem = Problem()
        g1 = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), [], [2], [])
        g2 = Group(2,1,2,30,Availability({"mon":[12,13,14]}), [], [3], [])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_teacher(Teacher(3,"Krzysztof Nowak", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({"mon":[10,11,12,13,14]}), []))
        problem.add_cluster(Cluster([2], [1,2]))
        problem.add_record(Record(1, [2], 3, "mon", 10))

        # Should return [] since it possible to place g2 but not in the same 'cluster' where g1 is
        placements = get_all_placements_for_group(g2, problem)
        self.assertEqual(placements, [])

    def test_getAllPlacementsForGroup_should_use_few_cluster_blocks_if_needed(self):
        problem = Problem()
        g1 = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), [], [2], [])
        g2 = Group(1,1,2,30,Availability({"tue":[12,13,14]}), [], [2], [])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15], "tue":[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({"mon":[10,11,12,13,14], "tue":[10,11,12,13,14,15]}), []))
        problem.add_cluster(Cluster([2,2], [1,2]))
        problem.add_record(Record(1, [2], 3, "mon", 10))

        # Should find placements since 2 blocks in cluster are available
        # (one class is assigned at monday and other one has availability only on tuesday)
        placements = get_all_placements_for_group(g2, problem)
        self.assertEqual(len(placements), 2)

    # TODO:
    def test_getAllPlacementsForGroup_should_use_few_cluster_blocks_for_one_day_if_needed(self):
        problem = Problem()
        g1 = Group(1,1,2,30,Availability({"mon":[10,11]}), [], [2], [])
        g2 = Group(2,1,2,30,Availability({"mon":[14,15]}), [], [2], [])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]})))
        problem.add_room(Room(3, 34, Availability({"mon":[10,11,12,13,14,15]}), []))
        problem.add_cluster(Cluster([2,2], [1,2]))
        problem.add_record(Record(1, [2], 3, "mon", 10))

        # Should  find placement for g2 since it possible to 2 two h-long blocks on one day are satysfying the cluster
        placements = get_all_placements_for_group(g2, problem)
        self.assertEqual(len(placements), 1)

    def test_getAllPlacementsForGroup_should_find_all_placements(self):
        problem = Problem()
        g1 = Group(1,1,2,30,Availability({"mon":[10,11,12,13,14]}), [], [2], [1,3])
        g2 = Group(2,1,2,30,Availability({"mon":[12,13,14,15]}), [], [2], [1,3])
        problem.add_group(g1)
        problem.add_group(g2)
        problem.add_teacher(Teacher(2,"Jan Kowalski", 90, Availability({"mon":[10,11,12,13,14,15]}, {("mon", 10) : [2,4],
                                                                                                      ("mon", 11) : [2,4],
                                                                                                      ("mon", 12) : [2,4],
                                                                                                      ("mon", 13) : [2,4],
                                                                                                      ("mon", 14) : [2,4]})))
        problem.add_room(Room(3, 30, Availability({"mon":[10,11,12,13,14]}), []))
        problem.add_cluster(Cluster([5], [1,2]))
        problem.add_record(Record(1, [2], 3, "mon", 10))

        placements = get_all_placements_for_group(g2, problem)
        # Should find all placements (mon 12 and 13, not at mon 14 because cluster range is 5h long)
        self.assertEqual(len(placements), 2)

    def test_get_best_record(self):
        def rating_function_stub(r: Record, p: Problem):
            # the later the better but not monday
            if r.day == "mon":
                return 0
            return r.hour 
        
        problem = Problem()
        placements = [
            (3, [11], [[25],[11]], "mon", 10, []),
            (3, [11], [[25],[11]], "mon", 18, []),
            (3, [11], [[25],[11]], "tue", 17, []),
            (3, [11], [[25],[11]], "tue", 16, []),
            (3, [11], [[25],[11]], "wed", 15, []),
            (3, [11], [[25],[11]], "mon", 20, []),
        ]

        chosen_record = get_best_record(placements, problem, rating_function_stub)
        self.assertEqual(Record(3,[11],[25,11],"tue",17), chosen_record)

