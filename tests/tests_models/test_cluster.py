from src.models import Cluster, Allocation
import unittest

class TestCluster(unittest.TestCase):
    def test_from_json(self):
        data = """
        {
            "id" : 1,
            "range": [2,2],
            "group_ids": [17,18]
        }
        """
        
        cluster = Cluster.from_json(data)

        self.assertEqual(cluster.id, 1)
        self.assertEqual(cluster.range, [2,2])
        self.assertEqual(cluster.group_ids, [17,18])

    def test_not_int_in_range_throws(self):
        data = """
        {
            "id" : 1,
            "range": ["abc",2],
            "group_ids": [17,18]
        }
        """
        
        with self.assertRaises(ValueError) as err:
            Cluster.from_json(data)

        self.assertIn("range", str(err.exception))
        self.assertIn("abc", str(err.exception))
    
    def test_missing_field_throws(self):
        data = """
        {
            "id" : 1,
            "group_ids": [17,18]
        }
        """
        
        with self.assertRaises(KeyError) as err:
            Cluster.from_json(data)

        self.assertIn("missing", str(err.exception))
        self.assertIn("range", str(err.exception))

    def test_can_create_cluster_with_empty_range_with_from_json(self):
        data = """
        {
            "id" : 1,
            "range": [],
            "group_ids": [17,18]
        }
        """
        c = Cluster.from_json(data)

        self.assertEqual(c.id, 1)
        self.assertEqual(c.range, [])
        self.assertEqual(c.group_ids, [17,18])

    def test_can_create_cluster_with_empty_range_with_init(self):
        c = Cluster(1, [], [17,18])
        self.assertEqual(c.id, 1)
        self.assertEqual(c.range, [])
        self.assertEqual(c.group_ids, [17,18])

    def test_cluster_check_general(self):
        allocs = [
            Allocation(1, [], 1, [10,11]),
            Allocation(2, [], 1, [12,13]),
            Allocation(3, [], 2, [10,11])
        ]

        cs = [
            Cluster(7, [1], [1,2,3]),
            Cluster(7, [2], [1,2,3]),
            Cluster(7, [4], [1,2,3]),
            Cluster(7, [2,2], [1,2,3]),
            Cluster(7, [2,4], [1,2,3]),
            Cluster(7, [2,2,2], [1,2,3]),
        ]

        for c in cs:
            for a in allocs:
                c.add_allocation(a)

        self.assertFalse(cs[0].check())
        self.assertFalse(cs[1].check())
        self.assertFalse(cs[2].check())
        self.assertFalse(cs[3].check())

        self.assertTrue(cs[4].check())
        self.assertTrue(cs[5].check())

    def test_cluster_check_short_hours(self):
        allocs = [
            Allocation(1, [], 1, [10,11]),
            Allocation(2, [], 1, [10,11])
        ]

        cs = [
            Cluster(7, [1], [1,2]),
            Cluster(7, [2], [1,2])
        ]

        for c in cs:
            for a in allocs:
                c.add_allocation(a)

        self.assertFalse(cs[0].check())
        self.assertTrue(cs[1].check())

    def test_cluster_check_with_empty_range(self):
        allocs = [
            Allocation(1, [], 1, [10,11]),
            Allocation(2, [], 1, [10,11]),
            Allocation(3, [], 2, [12,13])
        ]

        cs = [
            Cluster(7, [], [1,2]),
            Cluster(7, [], [2,3])
        ]

        for c in cs:
            for a in allocs:
                c.add_allocation(a)

        self.assertFalse(cs[0].check())
        self.assertTrue(cs[1].check())