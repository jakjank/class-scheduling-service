import unittest
from backend.src import Course

class TestCourse(unittest.TestCase):
    def test_from_json(self):
        data = """
        {  
            "id": 17,
            "name": "MDM"
        }
        """

        course = Course.from_json(data)

        self.assertEqual(course.id, 17)
        self.assertEqual(course.name, 'MDM')

if __name__ == '__main__':
    unittest.main()