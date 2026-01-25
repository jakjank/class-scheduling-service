from src import Cluster
import unittest

class TestCluster(unittest.TestCase):
    def test_from_json(self):
        data = """
        {
            "range": [2,2],
            "groups_ids": [17,18]
        }
        """
        
        cluster = Cluster.from_json(data)

        self.assertEqual(cluster.range, [2,2])
        self.assertEqual(cluster.groups_ids, [17,18])

    def test_not_int_range_throws(self):
        data = """
        {
            "range": ["abc",2],
            "groups_ids": [17,18]
        }
        """
        
        with self.assertRaises(ValueError) as err:
            Cluster.from_json(data)

        self.assertIn("range", str(err.exception))
        self.assertIn("abc", str(err.exception))
    
    def test_missing_field_throws(self):
        data = """
        {
            "groups_ids": [17,18]
        }
        """
        
        with self.assertRaises(KeyError) as err:
            Cluster.from_json(data)

        self.assertIn("missing", str(err.exception))
        self.assertIn("range", str(err.exception))

    def test_can_create_cluster_with_empty_range_with_from_json(self):
        data = """
        {
            "range": [],
            "groups_ids": [17,18]
        }
        """
        c = Cluster.from_json(data)
        self.assertEqual(c.range, [])
        self.assertEqual(c.groups_ids, [17,18])

    def test_can_create_cluster_with_empty_range_with_init(self):
        c = Cluster([], [17,18])
        self.assertEqual(c.range, [])
        self.assertEqual(c.groups_ids, [17,18])