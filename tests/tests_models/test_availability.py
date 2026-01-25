from src import Availability
import unittest

class TestAvailability(unittest.TestCase):
    def test_from_json(self):
        data = """
        {
            "1": [],
            "2": [10,11,12,13,14,15,16],
            "3": [],
            "4": [18,19],
            "5": [8,9,10,11,12],
            "6": [],
            "7": []
        }
        """

        avail = Availability.from_json(data)

        self.assertEqual(avail.slots[1], [])
        self.assertEqual(avail.slots[2], [10,11,12,13,14,15,16])
        self.assertEqual(avail.slots[3], [])
        self.assertEqual(avail.slots[4], [18,19])
        self.assertEqual(avail.slots[5], [8,9,10,11,12])
        self.assertEqual(avail.slots[6], [])
        self.assertEqual(avail.slots[7], [])

    
    def test_bad_day_throws(self):
        data = """
        {
            "1": [],
            "2": [10,11,12,13,14,15,16],
            "3": [],
            "4": [18,19],
            "5": [8,9,10,11,12],
            "6": [],
            "8": []
        }
        """

        with self.assertRaises(ValueError) as err:
            Availability.from_json(data)

        self.assertIn("key", str(err.exception))
        self.assertIn("8", str(err.exception))

    def test_bad_slot_throws(self):
        data = """
        {
            "1": [],
            "2": [-2,10,11,12,13,24,15,16],
            "3": [],
            "4": [18,19],
            "5": [8,9,10,11,12],
            "6": [],
            "7": []
        }
        """

        with self.assertRaises(ValueError) as err:
            Availability.from_json(data)
        
        self.assertIn("'-2'", str(err.exception))
    
    def test_init_from_dict(self):
        dir = {1 : [],
               2 : [10,11,12,13,14,15,16],
               3 : [],
               4 : [18,19],
               5 : [8,9,10,11,12],
               7 : []}
        
        avail = Availability(dir)

        self.assertEqual(avail.slots[1], [])
        self.assertEqual(avail.slots[2], [10,11,12,13,14,15,16])
        self.assertEqual(avail.slots[3], [])
        self.assertEqual(avail.slots[4], [18,19])
        self.assertEqual(avail.slots[5], [8,9,10,11,12])
        self.assertEqual(avail.slots[6], [])
        self.assertEqual(avail.slots[7], [])

    def test_remove_slot_without_mask(self):
        avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        
        # Remove slot 10 completely (no mask)
        result = avail.remove(1, 10, [])
        
        self.assertTrue(result)
        self.assertEqual(avail.slots[1], [11, 12])
        self.assertNotIn((1, 10), avail.taken_periods)

    def test_remove_slot_with_mask(self):
        avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        
        # Remove slot 10 for periods [1, 3] (odd weeks)
        result = avail.remove(1, 10, [1, 3])
        
        self.assertTrue(result)
        self.assertEqual(avail.slots[1], [10, 11, 12])  # Hour still exists
        self.assertEqual(avail.taken_periods[(1, 10)], [1, 3])

    def test_remove_nonexisting_slot(self):
        avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        
        # Try to remove slot that doesn't exist in avail
        result = avail.remove(1, 15, [])
        
        self.assertFalse(result)
        self.assertEqual(avail.slots[1], [10, 11, 12])

    def test_remove_with_conflicting_mask(self):
        avail = Availability(
            {1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            {(1, 10): [1, 3]}  # Already taken for odd weeks
        )
        
        # Try to remove with overlapping mask
        result = avail.remove(1, 10, [1, 2])
        
        self.assertFalse(result)
        self.assertEqual(avail.taken_periods[(1, 10)], [1, 3])

    def test_remove_with_non_conflicting_mask(self):
        avail = Availability(
            {1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            {(1, 10): [1, 3]}  # Already taken for odd weeks
        )
        
        # Remove with non-overlapping mask (even weeks)
        result = avail.remove(1, 10, [2, 4])
        
        self.assertTrue(result)
        self.assertEqual(avail.taken_periods[(1, 10)], [1, 3, 2, 4])

    def test_remove_multiple_times_with_masks(self):
        avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        
        # First removal
        result1 = avail.remove(1, 10, [1])
        self.assertTrue(result1)
        self.assertEqual(avail.taken_periods[(1, 10)], [1])
        
        # Second removal
        result2 = avail.remove(1, 10, [3])
        self.assertTrue(result2)
        self.assertEqual(avail.taken_periods[(1, 10)], [1, 3])
        
        # Third removal
        result3 = avail.remove(1, 10, [5])
        self.assertTrue(result3)
        self.assertEqual(avail.taken_periods[(1, 10)], [1, 3, 5])
