from src.models import Allocation
import unittest

class TestAllocation(unittest.TestCase):
    def test_from_json(self):
        data = """
        {
            "group_id": 1,
            "teacher_ids": [1],
            "room_ids": [32],
            "day": 1,
            "slots": [8,9]
        }
        """
        
        alloc = Allocation.from_json(data)

        self.assertEqual(alloc.group_id, 1)
        self.assertEqual(alloc.room_ids, [32])
        self.assertEqual(alloc.day, 1)
        self.assertEqual(alloc.slots, [8,9])

    def test_bad_day_format_throws(self):
        data = """
        {
            "group_id": 1,
            "teacher_ids": [1],
            "room_ids": [32],
            "day": 9,
            "slots": [8]
        }
        """
        
        with self.assertRaises(ValueError) as err:
            Allocation.from_json(data)

        self.assertIn("9", str(err.exception))

    def test_bad_slot_throws(self):
        data = """
        {
            "group_id": 1,
            "teacher_ids": [1],
            "room_ids": [32],
            "day": 1,
            "slots": ["abc",1]
        }
        """
        
        with self.assertRaises(ValueError) as err:
            Allocation.from_json(data)

        self.assertIn("abc", str(err.exception))
    
    def test_bad_slot_throws_2(self):
        data = """
        {
            "group_id": 1,
            "teacher_ids": [1],
            "room_ids": [32],
            "day": 1,
            "slots": [-24]
        }
        """
        
        with self.assertRaises(ValueError) as err:
            Allocation.from_json(data)

        self.assertIn("slot", str(err.exception))
        self.assertIn("-24", str(err.exception))

    def test_missing_field_throws(self):
        data = """
        {
            "group_id": 1,
            "teacher_ids": [1],
            "room_ids": [32],
            "slot": [12]
        }
        """
        
        with self.assertRaises(KeyError) as err:
            Allocation.from_json(data)

        self.assertIn("missing", str(err.exception))
        self.assertIn("day", str(err.exception))
