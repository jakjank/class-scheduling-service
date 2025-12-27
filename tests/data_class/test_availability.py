import unittest
from backend.src import Availability

class TestAvailability(unittest.TestCase):
    def test_from_json(self):
        data = '{ \
            "mon": [],\
            "tue": [10,11,12,13,14,15,16],\
            "wed": [],\
            "thu": [18,19],\
            "fri": [8,9,10,11,12],\
            "sat": [],\
            "sun": []\
        }'

        avail = Availability.from_json(data)

        self.assertEqual(avail.hours['mon'], [])
        self.assertEqual(avail.hours['tue'], [10,11,12,13,14,15,16])
        self.assertEqual(avail.hours['wed'], [])
        self.assertEqual(avail.hours['thu'], [18,19])
        self.assertEqual(avail.hours['fri'], [8,9,10,11,12])
        self.assertEqual(avail.hours['sat'], [])
        self.assertEqual(avail.hours['sun'], [])

    
    def test_bad_day_throws(self):
        data = '{ \
            "mon": [],\
            "tue": [10,11,12,13,14,15,16],\
            "wed": [],\
            "thu": [18,19],\
            "frii": [8,9,10,11,12],\
            "sat": [],\
            "sun": []\
        }'

        with self.assertRaises(ValueError):
            Availability.from_json(data)

    def test_bad_hour_throws(self):
        data = '{ \
            "mon": [],\
            "tue": [10,11,12,13,24,15,16],\
            "wed": [],\
            "thu": [18,19],\
            "frii": [8,9,10,11,12],\
            "sat": [],\
            "sun": []\
        }'

        with self.assertRaises(ValueError):
            Availability.from_json(data)
    
    def test_init_from_dict(self):
        dir = {'mon' : [],
               'tue' : [10,11,12,13,14,15,16],
               'wed' : [],
               'thu' : [18,19],
               'fri' : [8,9,10,11,12],
               'sat' : [],
               'sun' : []}
        
        avail = Availability(dir)

        self.assertEqual(avail.hours['mon'], [])
        self.assertEqual(avail.hours['tue'], [10,11,12,13,14,15,16])
        self.assertEqual(avail.hours['wed'], [])
        self.assertEqual(avail.hours['thu'], [18,19])
        self.assertEqual(avail.hours['fri'], [8,9,10,11,12])
        self.assertEqual(avail.hours['sat'], [])
        self.assertEqual(avail.hours['sun'], [])

    def test_remove_hour_without_mask(self):
        avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        # Remove hour 10 completely (no mask)
        result = avail.remove('mon', 10, [])
        
        self.assertTrue(result)
        self.assertEqual(avail.hours['mon'], [11, 12])
        self.assertNotIn(('mon', 10), avail.taken_periods)

    def test_remove_hour_with_mask(self):
        avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        # Remove hour 10 for periods [1, 3] (odd weeks)
        result = avail.remove('mon', 10, [1, 3])
        
        self.assertTrue(result)
        self.assertEqual(avail.hours['mon'], [10, 11, 12])  # Hour still exists
        self.assertEqual(avail.taken_periods[('mon', 10)], [1, 3])

    def test_remove_nonexistent_hour(self):
        avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        # Try to remove hour that doesn't exist
        result = avail.remove('mon', 15, [])
        
        self.assertFalse(result)
        self.assertEqual(avail.hours['mon'], [10, 11, 12])

    def test_remove_with_conflicting_mask(self):
        avail = Availability(
            {'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []},
            {('mon', 10): [1, 3]}  # Already taken for odd weeks
        )
        
        # Try to remove with overlapping mask
        result = avail.remove('mon', 10, [1, 2])
        
        self.assertFalse(result)
        self.assertEqual(avail.taken_periods[('mon', 10)], [1, 3])

    def test_remove_with_non_conflicting_mask(self):
        avail = Availability(
            {'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []},
            {('mon', 10): [1, 3]}  # Already taken for odd weeks
        )
        
        # Remove with non-overlapping mask (even weeks)
        result = avail.remove('mon', 10, [2, 4])
        
        self.assertTrue(result)
        self.assertEqual(avail.taken_periods[('mon', 10)], [1, 3, 2, 4])

    def test_remove_multiple_times_with_masks(self):
        avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        
        # First removal
        result1 = avail.remove('mon', 10, [1])
        self.assertTrue(result1)
        self.assertEqual(avail.taken_periods[('mon', 10)], [1])
        
        # Second removal
        result2 = avail.remove('mon', 10, [3])
        self.assertTrue(result2)
        self.assertEqual(avail.taken_periods[('mon', 10)], [1, 3])
        
        # Third removal
        result3 = avail.remove('mon', 10, [5])
        self.assertTrue(result3)
        self.assertEqual(avail.taken_periods[('mon', 10)], [1, 3, 5])


if __name__ == '__main__':
    unittest.main()