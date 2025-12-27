import unittest
from backend.src import Cluster

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