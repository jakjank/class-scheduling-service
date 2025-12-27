import unittest
from backend.src import Room, Availability

class TestRoom(unittest.TestCase):
    def test_from_json(self):
        data = """
            {"id" : 32,
            "capacity" : 24,
            "availability" : {
                "mon": [],
                "tue": [10,11,12,13,14,15,16],
                "wed": [],
                "thu": [18,19],
                "fri": [8,9,10,11,12],
                "sat": [],
                "sun": []
                },
            "labels" : ["LAB", "CLASS", "TV"]
            }
            """
        
        room = Room.from_json(data)

        self.assertEqual(room.id, 32)
        self.assertEqual(room.capacity, 24)
        self.assertEqual(room.availability.hours['mon'], [])
        self.assertEqual(room.availability.hours['tue'], [10,11,12,13,14,15,16])
        self.assertEqual(room.availability.hours['wed'], [])
        self.assertEqual(room.availability.hours['thu'], [18,19])
        self.assertEqual(room.availability.hours['fri'], [8,9,10,11,12])
        self.assertEqual(room.availability.hours['sat'], [])
        self.assertEqual(room.availability.hours['sun'], [])
        self.assertEqual(
            room.labels,
            ["LAB", "CLASS", "TV"]
        )

    def test_book_time_slot_without_mask(self):
        room_avail = Availability({'mon': [8, 9, 10], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room = Room(id=101, capacity=30, availability=room_avail, labels=["LAB"])
        
        # Reserve Monday at 9:00 with no period mask
        room.book_time_slot('mon', 9, [])
        
        # Check that hour 9 was removed from Monday
        self.assertEqual(room.availability.hours['mon'], [8, 10])
        self.assertNotIn(('mon', 9), room.availability.taken_periods)

    def test_book_time_slot_with_mask(self):
        room_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room = Room(id=102, capacity=50, availability=room_avail, labels=["LECTURE_HALL"])
        
        # Reserve Monday at 10:00 with period mask [2, 4] (even weeks)
        room.book_time_slot('mon', 10, [2, 4])
        
        # Check that hour 10 still exists but has taken_periods
        self.assertEqual(room.availability.hours['mon'], [10, 11, 12])
        self.assertEqual(room.availability.taken_periods[('mon', 10)], [2, 4])

    def test_book_time_slot_multiple_times(self):
        room_avail = Availability({'mon': [14, 15, 16], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        room = Room(id=103, capacity=25, availability=room_avail, labels=["CLASS"])
        
        # Reserve hour 15 for week 1
        room.book_time_slot('mon', 15, [1])
        
        # Reserve hour 15 for week 2
        room.book_time_slot('mon', 15, [2])
        
        # Check that hour 15 is still available but periods 1 and 2 are taken
        self.assertEqual(room.availability.hours['mon'], [14, 15, 16])
        self.assertEqual(room.availability.taken_periods[('mon', 15)], [1, 2])

if __name__ == '__main__':
    unittest.main()