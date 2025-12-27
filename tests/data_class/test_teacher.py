import unittest
from backend.src import Teacher, Availability

class TestTeacher(unittest.TestCase):
    def test_from_json(self):
        data = """
        {   
            "id": 1,
            "name": "John Doe",
            "quota": 10,
            "availability": {"mon": [8,9,10,11], "fri": [12,13]}
        }
        """

        teacher = Teacher.from_json(data)

        self.assertEqual(teacher.id, 1)
        self.assertEqual(teacher.name, 'John Doe')
        self.assertEqual(teacher.quota, 10)
        self.assertEqual(teacher.availability.hours, {'mon': [8,9,10,11], 
                                                      'tue': [],
                                                      'wed': [],
                                                      'thu': [],
                                                      "fri": [12,13],
                                                      'sat': [],
                                                      'sun': []})

    def test_book_time_slot_without_mask(self):
        teacher_avail = Availability({'mon': [8, 9, 10, 11], 'tue': [], 'wed': [], 'thu': [], 'fri': [12, 13], 'sat': [], 'sun': []})
        teacher = Teacher(id=1, name="John Doe", quota=10, availability=teacher_avail)
        
        # Reserve Monday at 9:00 with no period mask
        teacher.book_time_slot('mon', 9, [])
        
        # Check that hour 9 was removed from Monday
        self.assertEqual(teacher.availability.hours['mon'], [8, 10, 11])
        self.assertNotIn(('mon', 9), teacher.availability.taken_periods)

    def test_book_time_slot_with_mask(self):
        teacher_avail = Availability({'mon': [10, 11, 12], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        teacher = Teacher(id=2, name="Jane Smith", quota=15, availability=teacher_avail)
        
        # Reserve Monday at 10:00 with period mask [1, 3] (odd weeks)
        teacher.book_time_slot('mon', 10, [1, 3])
        
        # Check that hour 10 still exists but has taken_periods
        self.assertEqual(teacher.availability.hours['mon'], [10, 11, 12])
        self.assertEqual(teacher.availability.taken_periods[('mon', 10)], [1, 3])

    def test_book_time_slot_multiple_times(self):
        teacher_avail = Availability({'mon': [8, 9, 10], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []})
        teacher = Teacher(id=3, name="Bob Johnson", quota=20, availability=teacher_avail)
        
        # Reserve hour 9 for week 1
        teacher.book_time_slot('mon', 9, [1])
        
        # Reserve hour 9 for week 3
        teacher.book_time_slot('mon', 9, [3])
        
        # Check that hour 9 is still available but periods 1 and 3 are taken
        self.assertEqual(teacher.availability.hours['mon'], [8, 9, 10])
        self.assertEqual(teacher.availability.taken_periods[('mon', 9)], [1, 3])

if __name__ == '__main__':
    unittest.main()