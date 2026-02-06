from src.models import Group
import unittest

class TestGroup(unittest.TestCase):
    def test_from_json(self):
        data = """
        {
            "id": 32,
            "duration": 2,
            "capacity": 24,
            "availability": {"1": [8,9,10,11], "5": [12,13]},
            "labels": [[["LAB"], ["CLASS", "TV"]]],
            "teacher_ids": [2, 17]
        }
        """
        
        group = Group.from_json(data)

        self.assertEqual(group.id, 32)
        self.assertEqual(group.duration, 2)
        self.assertEqual(group.capacity, 24)
        self.assertEqual(group.availability.slots, {1: [8,9,10,11], 
                                                      2: [],
                                                      3: [],
                                                      4: [],
                                                      5: [12,13],
                                                      6: [],
                                                      7: []})
        self.assertEqual(
            group.labels,
            [[["LAB"], ["CLASS", "TV"]]]
        )
        self.assertEqual(
            group.teacher_ids,
            [2,17]
        )
        self.assertEqual(group.occurrence_desc, [])

    def test_from_json_with_occurrence_desc(self):
        data = """
        {
            "id": 32,
            "duration": 2,
            "capacity": 24,
            "availability": {"1": [8,9,10,11], "5": [12,13]},
            "labels": [[["LAB"], ["CLASS", "TV"]],[["PROJECTOR"]]],
            "teacher_ids": [2, 17],
            "occurrence_desc": [1, 2, 7]
        }
        """
        
        group = Group.from_json(data)

        self.assertEqual(group.id, 32)
        self.assertEqual(group.duration, 2)
        self.assertEqual(group.capacity, 24)
        self.assertEqual(group.availability.slots, {1: [8,9,10,11], 
                                                      2: [],
                                                      3: [],
                                                      4: [],
                                                      5: [12,13],
                                                      6: [],
                                                      7: []})
        self.assertEqual(
            group.labels,
            [[["LAB"], ["CLASS", "TV"]],[["PROJECTOR"]]]
        )
        self.assertEqual(
            group.teacher_ids,
            [2,17]
        )
        self.assertEqual(group.occurrence_desc, [1,2,7])


    def test_duration_not_int_throws(self):
        data = """
        {
            "id": 32,
            "duration": "abc",
            "capacity": 24,
            "availability": {"1": [8,9,10,11], "5": [12,13]},
            "labels": [[["LAB"], ["CLASS", "TV"]]],
            "teacher_ids": [2, 17]
        }
        """

        with self.assertRaises(ValueError) as err:
            Group.from_json(data)

        self.assertIn("duration", str(err.exception))
        self.assertIn("abc", str(err.exception))

    def test_capacity_not_int_throws(self):
        data = """
        {
            "id": 32,
            "duration": 2,
            "capacity": "abc",
            "availability": {"1": [8,9,10,11], "5": [12,13]},
            "labels": [[["LAB"], ["CLASS", "TV"]]],
            "teacher_ids": [2, 17]
        }
        """

        with self.assertRaises(ValueError) as err:
            Group.from_json(data)

        self.assertIn("capacity", str(err.exception))
        self.assertIn("abc", str(err.exception))

    def test_missing_field_throws(self):
        data = """
        {
            "id": 32,
            "duration": 2,
            "capacity": 24,
            "labels": [[["LAB"], ["CLASS", "TV"]]],
            "teacher_ids": [2, 17]
        }
        """
        
        with self.assertRaises(KeyError) as err:
            Group.from_json(data)

        self.assertIn("missing", str(err.exception))
        self.assertIn("availability", str(err.exception))

    def test_are_labels_valid_properly_checks_empty_labels(self):
        self.assertTrue(Group.are_labels_valid([]))

    def test_are_labels_valid_properly_checks_ok__simple_example(self):
        # This labels require 1 room tag1
        self.assertTrue(Group.are_labels_valid([[['tag1']]]))

    def test_are_labels_valid_properly_checks_ok_example(self):
        # This labels require 2 rooms
        # One with label tag1 and tag2 or just tag3 
        # Second with only tag4 
        self.assertTrue(Group.are_labels_valid([ [['tag1','tag2'],['tag3']] ,[['tag4']]]))

    def test_are_labels_valid_properly_checks_bad_simple_examples(self):
        self.assertFalse(Group.are_labels_valid([['tag1']]))
        self.assertFalse(Group.are_labels_valid([[[1]]]))

    def test_are_labels_valid_properly_checks_bad_hard_examples(self):
        self.assertFalse(Group.are_labels_valid([[['tag1','tag2'],'tag3'],[['tag4']]]))
        self.assertFalse(Group.are_labels_valid([['tag1','tag2','tag3'],[['tag4']]]))
        self.assertFalse(Group.are_labels_valid([[['tag1','tag2'],['tag3']],['tag4']]))

    def test_from_json_fail_with_bad_labels(self):
        data = """
        {
            "id": 32,
            "duration": 2,
            "capacity": 24,
            "availability": {"1": [8,9,10,11], "5": [12,13]},
            "labels": [[['tag1', 'tag2'] ,['tag3']], ['tag4']],
            "teacher_ids": [2, 17],
            "occurrence_desc": [1, 2, 7]
        }
        """

        with self.assertRaises(ValueError) as err:
            Group.from_json(data)
        
        # self.assertIn("[[['tag1', 'tag2'] ,['tag3']], ['tag4']]", str(err.exception))

    def test_from_json_throws_when_no_teachers(self):
        Group.THROW_IF_NO_TEACHER = True
        data = """
            {
                "id": 1,
                "duration": 2,
                "capacity": 24,
                "availability": {"1": [8,9,10,11]},
                "labels": [[["CLASS"]]],
                "teacher_ids": []
            }
        """

        with self.assertRaises(ValueError) as err:
            Group.from_json(data)

        self.assertIn("teacher", str(err.exception))
    
    def test_from_json_throws_when_no_teachers_field(self):
        Group.THROW_IF_NO_TEACHER = True
        data = """
            {
                "id": 1,
                "duration": 2,
                "capacity": 24,
                "availability": {"1": [8,9,10,11]},
                "labels": [[["CLASS"]]]
            }
        """

        with self.assertRaises(ValueError) as err:
            Group.from_json(data)

        self.assertIn("teacher", str(err.exception))
