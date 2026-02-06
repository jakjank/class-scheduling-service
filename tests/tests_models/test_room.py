from src.models import Room, Availability
import unittest

class TestRoom(unittest.TestCase):
    def test_from_json(self):
        data = """
            {"id" : 32,
            "capacity" : 24,
            "availability" : {
                "2": [10,11,12,13,14,15,16],
                "4": [18,19],
                "5": [8,9,10,11,12]
                },
            "labels" : ["LAB", "CLASS", "TV"]
            }
            """
        
        room = Room.from_json(data)

        self.assertEqual(room.id, 32)
        self.assertEqual(room.capacity, 24)
        self.assertEqual(room.availability.slots[1], [])
        self.assertEqual(room.availability.slots[2], [10,11,12,13,14,15,16])
        self.assertEqual(room.availability.slots[3], [])
        self.assertEqual(room.availability.slots[4], [18,19])
        self.assertEqual(room.availability.slots[5], [8,9,10,11,12])
        self.assertEqual(room.availability.slots[6], [])
        self.assertEqual(room.availability.slots[7], [])
        self.assertEqual(
            room.labels,
            ["LAB", "CLASS", "TV"]
        )

    def test_book_time_slot_without_mask(self):
        room_avail = Availability({1: [8, 9, 10], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        room = Room(id=101, capacity=30, availability=room_avail, labels=["LAB"])
        
        # Reserve Monday at 9:00 with no period mask
        room.book_time_slot(1, 9, [])
        
        # Check that slot 9 was removed from Monday
        self.assertEqual(room.availability.slots[1], [8, 10])
        self.assertNotIn((1, 9), room.availability.taken_periods)

    def test_book_time_slot_with_mask(self):
        room_avail = Availability({1: [10, 11, 12], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        room = Room(id=102, capacity=50, availability=room_avail, labels=["LECTURE_HALL"])
        
        # Reserve Monday at 10:00 with period mask [2, 4] (even weeks)
        room.book_time_slot(1, 10, [2, 4])
        
        # Check that slot 10 still exists but has taken_periods
        self.assertEqual(room.availability.slots[1], [10, 11, 12])
        self.assertEqual(room.availability.taken_periods[(1, 10)], [2, 4])

    def test_book_time_slot_multiple_times(self):
        room_avail = Availability({1: [14, 15, 16], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
        room = Room(id=103, capacity=25, availability=room_avail, labels=["CLASS"])
        
        # Reserve slot 15 for week 1
        room.book_time_slot(1, 15, [1])
        
        # Reserve slot 15 for week 2
        room.book_time_slot(1, 15, [2])
        
        # Check that slot 15 is still available but periods 1 and 2 are taken
        self.assertEqual(room.availability.slots[1], [14, 15, 16])
        self.assertEqual(room.availability.taken_periods[(1, 15)], [1, 2])

    def test_capacity_not_int_throws(self):
        data = """
        {
            "id" : 32,
            "capacity" : "abc",
            "availability" : {
                "2": [10,11,12,13,14,15,16],
                "4": [18,19],
                "5": [8,9,10,11,12]
                },
            "labels" : ["LAB", "CLASS", "TV"]
        }
        """

        with self.assertRaises(ValueError) as err:
            Room.from_json(data)

        self.assertIn("capacity", str(err.exception))
        self.assertIn("abc", str(err.exception))

    def test_missing_field_throws(self):
        data = """
        {
            "id" : 32,
            "availability" : {
                "2": [10,11,12,13,14,15,16],
                "4": [18,19],
                "5": [8,9,10,11,12]
                },
            "labels" : ["LAB", "CLASS", "TV"]
        }
        """
        
        with self.assertRaises(KeyError) as err:
            Room.from_json(data)

        self.assertIn("missing", str(err.exception))
        self.assertIn("capacity", str(err.exception))

    def test_satisfies_labels(self):
        r = Room(3,30,Availability, ['tag1', 'tag2'])

        self.assertTrue(r.satisfies_labels_DNF([['tag1']]))
        self.assertTrue(r.satisfies_labels_DNF([['tag1'], ['tag2']]))
        self.assertTrue(r.satisfies_labels_DNF([['tag3'], ['tag1']]))
        self.assertFalse(r.satisfies_labels_DNF([['tag1','tag3'], ['tag2', 'tag4']]))
