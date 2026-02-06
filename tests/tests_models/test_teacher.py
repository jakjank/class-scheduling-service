from src.models import Teacher, Availability
import unittest

class TestTeacher(unittest.TestCase):
    def test_from_json(self):
        data = """
        {   
            "id": 1,
            "availability": {"1": [8,9,10,11], "5": [12,13]}
        }
        """

        teacher = Teacher.from_json(data)

        self.assertEqual(teacher.id, 1)
        self.assertEqual(teacher.availability.slots, {1: [8,9,10,11], 
                                                      2: [],
                                                      3: [],
                                                      4: [],
                                                      5: [12,13],
                                                      6: [],
                                                      7: []})

    def test_book_time_slot_without_mask(self):
        teacher_avail = Availability({1: [8, 9, 10, 11], 5: [12, 13]})
        teacher = Teacher(id=1, availability=teacher_avail)
        
        # Reserve Monday at 9:00 with no period mask
        teacher.book_time_slot(1, 9, [])
        
        # Check that slot 9 was removed from Monday
        self.assertEqual(teacher.availability.slots[1], [8, 10, 11])
        self.assertNotIn((1, 9), teacher.availability.taken_periods)

    def test_book_time_slot_with_mask(self):
        teacher_avail = Availability({1: [10, 11, 12]})
        teacher = Teacher(id=2, availability=teacher_avail)
        
        # Reserve Monday at 10:00 with period mask [1, 3] (odd weeks)
        teacher.book_time_slot(1, 10, [1, 3])
        
        # Check that slot 10 still exists but has taken_periods
        self.assertEqual(teacher.availability.slots[1], [10, 11, 12])
        self.assertEqual(teacher.availability.taken_periods[(1, 10)], [1, 3])

    def test_book_time_slot_multiple_times(self):
        teacher_avail = Availability({1: [8, 9, 10]})
        teacher = Teacher(id=3, availability=teacher_avail)
        
        # Reserve slot 9 for week 1
        teacher.book_time_slot(1, 9, [1])
        
        # Reserve slot 9 for week 3
        teacher.book_time_slot(1, 9, [3])
        
        # Check that slot 9 is still available but periods 1 and 3 are taken
        self.assertEqual(teacher.availability.slots[1], [8, 9, 10])
        self.assertEqual(teacher.availability.taken_periods[(1, 9)], [1, 3])

    def test_missing_field_throws(self):
        data = """
        {
            "availability": {"1": [8,9,10,11], "5": [12,13]}
        }
        """
        
        with self.assertRaises(ValueError) as err:
            Teacher.from_json(data)

        self.assertIn("missing", str(err.exception))
        self.assertIn("id", str(err.exception))
