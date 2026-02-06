from src import Parser, Solver, ALGORITHMS_AVAILABLE
from src.models import Allocation, Group
import unittest
import os

class TestBig(unittest.TestCase):
    def test_big_parse(self):
        here = os.path.dirname(__file__)
        path = os.path.join(here, "big_problem.json")

        with open(path, "r") as f:
            data = f.read()

        parser = Parser()
        request = parser.parse(data)
        prob = request.problem
        self.assertEqual(len(prob.groups), 76)
        self.assertEqual(len(prob.teachers), 38)
        self.assertEqual(len(prob.rooms), 19)
        self.assertEqual(len(prob.clusters), 14)
        self.assertEqual(len(prob.allocations), 0)

    def test_big_solve(self):
        # This test may occasionally fail                               #
        # in such case try running this again and if this keeps failing #
        # then you broke smh :)                                         #

        for method in ALGORITHMS_AVAILABLE.keys():
            with self.subTest(f"SOLVE USING OPTION {method}"):
                here = os.path.dirname(__file__)
                path = os.path.join(here, "big_problem.json")

                with open(path, "r") as f:
                    data = f.read()

                tries = 20
                got_solution = False

                parser = Parser()
                solver = Solver()
                request = parser.parse(data)

                while(tries):
                    tries -= 1
                    response = solver.solve(request.problem, method)
                    if response.success:
                        got_solution = True
                        break
                self.assertTrue(got_solution)

    def test_big_check_success(self):
        here = os.path.dirname(__file__)
        path = os.path.join(here, "big_problem.json")

        with open(path, "r") as f:
            data = f.read()

        parser = Parser()
        request = parser.parse(data)
        prob = request.problem
        prob.allocations = [
            Allocation(group_id=1, room_ids=[30], day=4, slots=[16, 17]),
            Allocation(group_id=2, room_ids=[6], day=5, slots=[8, 9]),
            Allocation(group_id=3, room_ids=[7], day=1, slots=[12, 13]),
            Allocation(group_id=4, room_ids=[25], day=3, slots=[8, 9, 10]),
            Allocation(group_id=5, room_ids=[7], day=3, slots=[12, 13]),
            Allocation(group_id=6, room_ids=[6], day=2, slots=[14, 15]),
            Allocation(group_id=7, room_ids=[3], day=3, slots=[12, 13]),
            Allocation(group_id=8, room_ids=[2], day=2, slots=[14, 15]),
            Allocation(group_id=9, room_ids=[4], day=2, slots=[14, 15]),
            Allocation(group_id=10, room_ids=[7], day=1, slots=[8, 9]),
            Allocation(group_id=11, room_ids=[6], day=1, slots=[10, 11]),
            Allocation(group_id=12, room_ids=[9], day=3, slots=[8, 9, 10, 11]),
            Allocation(group_id=13, room_ids=[4], day=2, slots=[10, 11]),
            Allocation(group_id=14, room_ids=[5], day=2, slots=[12, 13]),
            Allocation(group_id=15, room_ids=[30], day=3, slots=[12, 13]),
            Allocation(group_id=16, room_ids=[7], day=2, slots=[10, 11]),
            Allocation(group_id=17, room_ids=[3], day=4, slots=[14, 15]),
            Allocation(group_id=18, room_ids=[8], day=3, slots=[14, 15]),
            Allocation(group_id=19, room_ids=[25], day=2, slots=[12, 13]),
            Allocation(group_id=20, room_ids=[25], day=3, slots=[14, 15]),
            Allocation(group_id=21, room_ids=[5], day=3, slots=[10, 11, 12]),
            Allocation(group_id=22, room_ids=[2], day=3, slots=[12, 13, 14]),
            Allocation(group_id=23, room_ids=[1], day=3, slots=[10, 11, 12]),
            Allocation(group_id=24, room_ids=[4], day=3, slots=[12, 13, 14]),
            Allocation(group_id=25, room_ids=[8], day=3, slots=[10, 11, 12]),
            Allocation(group_id=26, room_ids=[9], day=3, slots=[12, 13, 14]),
            Allocation(group_id=27, room_ids=[7], day=1, slots=[14, 15]),
            Allocation(group_id=28, room_ids=[7], day=4, slots=[12, 13]),
            Allocation(group_id=29, room_ids=[7], day=2, slots=[14, 15]),
            Allocation(group_id=30, room_ids=[1], day=3, slots=[8, 9]),
            Allocation(group_id=31, room_ids=[30], day=3, slots=[10, 11]),
            Allocation(group_id=32, room_ids=[9], day=2, slots=[8, 9]),
            Allocation(group_id=33, room_ids=[5], day=1, slots=[14, 15]),
            Allocation(group_id=34, room_ids=[1], day=1, slots=[14, 15]),
            Allocation(group_id=35, room_ids=[], day=1, slots=[12, 13]),
            Allocation(group_id=36, room_ids=[], day=2, slots=[14, 15]),
            Allocation(group_id=37, room_ids=[], day=3, slots=[14, 15]),
            Allocation(group_id=38, room_ids=[], day=1, slots=[12, 13]),
            Allocation(group_id=39, room_ids=[25], day=4, slots=[10, 11]),
            Allocation(group_id=40, room_ids=[5, 13], day=1, slots=[8, 9]),
            Allocation(group_id=41, room_ids=[8, 11], day=1, slots=[12, 13]),
            Allocation(group_id=42, room_ids=[8, 11], day=2, slots=[12, 13]),
            Allocation(group_id=43, room_ids=[9, 12], day=4, slots=[10, 11]),
            Allocation(group_id=44, room_ids=[7], day=2, slots=[12, 13]),
            Allocation(group_id=45, room_ids=[12], day=3, slots=[14, 15]),
            Allocation(group_id=46, room_ids=[30], day=4, slots=[10, 11, 12]),
            Allocation(group_id=47, room_ids=[2], day=3, slots=[10, 11]),
            Allocation(group_id=48, room_ids=[7], day=3, slots=[10, 11]),
            Allocation(group_id=49, room_ids=[6], day=3, slots=[10, 11]),
            Allocation(group_id=50, room_ids=[6], day=3, slots=[12, 13]),
            Allocation(group_id=51, room_ids=[3], day=3, slots=[14, 15]),
            Allocation(group_id=52, room_ids=[8], day=2, slots=[14, 15]),
            Allocation(group_id=53, room_ids=[1], day=2, slots=[12, 13]),
            Allocation(group_id=54, room_ids=[6], day=4, slots=[12, 13]),
            Allocation(group_id=55, room_ids=[1], day=4, slots=[14, 15]),
            Allocation(group_id=56, room_ids=[3], day=1, slots=[14, 15]),
            Allocation(group_id=57, room_ids=[25], day=1, slots=[14, 15]),
            Allocation(group_id=58, room_ids=[13], day=1, slots=[12, 13]),
            Allocation(group_id=59, room_ids=[10], day=4, slots=[10, 11]),
            Allocation(group_id=60, room_ids=[14], day=3, slots=[12, 13]),
            Allocation(group_id=61, room_ids=[16], day=1, slots=[12, 13]),
            Allocation(group_id=62, room_ids=[16], day=3, slots=[12, 13]),
            Allocation(group_id=63, room_ids=[5], day=4, slots=[10, 11]),
            Allocation(group_id=64, room_ids=[10], day=4, slots=[12, 13]),
            Allocation(group_id=65, room_ids=[13, 2], day=4, slots=[8]),
            Allocation(group_id=66, room_ids=[11, 3], day=4, slots=[8, 9]),
            Allocation(group_id=67, room_ids=[30], day=1, slots=[12, 13]),
            Allocation(group_id=68, room_ids=[14], day=1, slots=[10, 11]),
            Allocation(group_id=69, room_ids=[14], day=4, slots=[12, 13]),
            Allocation(group_id=70, room_ids=[3], day=2, slots=[14, 15]),
            Allocation(group_id=71, room_ids=[13], day=2, slots=[12, 13]),
            Allocation(group_id=72, room_ids=[15], day=4, slots=[14, 15]),
            Allocation(group_id=73, room_ids=[11], day=4, slots=[14, 15]),
            Allocation(group_id=74, room_ids=[13], day=4, slots=[12, 13]),
            Allocation(group_id=75, room_ids=[], day=3, slots=[10, 11]),
            Allocation(group_id=76, room_ids=[], day=3, slots=[8, 9]),
        ]
        msg = prob.check()
        self.assertEqual(msg, [])

    def test_big_check_fail(self):
        here = os.path.dirname(__file__)
        path = os.path.join(here, "big_problem.json")

        with open(path, "r") as f:
            data = f.read()

        parser = Parser()
        request = parser.parse(data)
        prob = request.problem
        prob.allocations = prob.allocations = [
            Allocation(group_id=1, room_ids=[30], day=4, slots=[16, 17]),
            Allocation(group_id=2, room_ids=[6], day=5, slots=[8, 9]),
            Allocation(group_id=3, room_ids=[7], day=1, slots=[12, 13]),
            Allocation(group_id=4, room_ids=[25], day=3, slots=[8, 9, 10]),
            Allocation(group_id=5, room_ids=[7], day=3, slots=[12, 13]),
            Allocation(group_id=6, room_ids=[6], day=2, slots=[14, 15]),
            Allocation(group_id=7, room_ids=[3], day=3, slots=[12, 13]),
            Allocation(group_id=8, room_ids=[2], day=2, slots=[14, 15]),
            Allocation(group_id=9, room_ids=[4], day=2, slots=[14, 15]),
            Allocation(group_id=10, room_ids=[7], day=1, slots=[8, 9]),
            Allocation(group_id=11, room_ids=[6], day=1, slots=[10, 11]),
            Allocation(group_id=12, room_ids=[9], day=3, slots=[8, 9, 10, 11]),
            Allocation(group_id=13, room_ids=[4], day=2, slots=[10, 11]),
            Allocation(group_id=14, room_ids=[5], day=2, slots=[12, 13]),
            Allocation(group_id=15, room_ids=[30], day=3, slots=[12, 13]),
            Allocation(group_id=16, room_ids=[7], day=2, slots=[10, 11]),
            Allocation(group_id=17, room_ids=[3], day=4, slots=[14, 15]),
            Allocation(group_id=18, room_ids=[8], day=3, slots=[14, 15]),
            Allocation(group_id=19, room_ids=[25], day=2, slots=[12, 13]),
            Allocation(group_id=20, room_ids=[25], day=3, slots=[14, 15]),
            Allocation(group_id=21, room_ids=[5], day=3, slots=[10, 11, 12]),
            Allocation(group_id=22, room_ids=[2], day=3, slots=[14, 15, 16]),
            Allocation(group_id=23, room_ids=[1], day=3, slots=[10, 11, 12]),
            Allocation(group_id=24, room_ids=[4], day=3, slots=[12, 13, 14]),
            Allocation(group_id=25, room_ids=[8], day=3, slots=[10, 11, 12]),
            Allocation(group_id=26, room_ids=[9], day=3, slots=[12, 13, 14]),
            Allocation(group_id=27, room_ids=[7], day=1, slots=[14, 15]),
            Allocation(group_id=28, room_ids=[7], day=4, slots=[12, 13]),
            Allocation(group_id=29, room_ids=[7], day=2, slots=[14, 15]),
            Allocation(group_id=30, room_ids=[1], day=3, slots=[8, 9]),
            Allocation(group_id=31, room_ids=[30], day=3, slots=[10, 11]),
            Allocation(group_id=32, room_ids=[9], day=2, slots=[8, 9]),
            Allocation(group_id=33, room_ids=[5], day=1, slots=[14, 15]),
            Allocation(group_id=34, room_ids=[1], day=1, slots=[14, 15]),
            Allocation(group_id=35, room_ids=[], day=1, slots=[12, 13]),
            Allocation(group_id=36, room_ids=[], day=2, slots=[14, 15]),
            Allocation(group_id=37, room_ids=[], day=3, slots=[14, 15]),
            Allocation(group_id=38, room_ids=[], day=1, slots=[12, 13]),
            Allocation(group_id=39, room_ids=[25], day=4, slots=[10, 11]),
            Allocation(group_id=40, room_ids=[5, 13], day=1, slots=[8, 9]),
            Allocation(group_id=41, room_ids=[8, 11], day=1, slots=[12, 13]),
            Allocation(group_id=42, room_ids=[8, 11], day=2, slots=[12, 13]),
            Allocation(group_id=43, room_ids=[9, 12], day=4, slots=[10, 11]),
            Allocation(group_id=44, room_ids=[7], day=2, slots=[12, 13]),
            Allocation(group_id=45, room_ids=[12], day=3, slots=[14, 15]),
            Allocation(group_id=46, room_ids=[30], day=4, slots=[10, 11, 12]),
            Allocation(group_id=47, room_ids=[2], day=3, slots=[10, 11]),
            Allocation(group_id=48, room_ids=[7], day=3, slots=[10, 11]),
            Allocation(group_id=49, room_ids=[6], day=3, slots=[10, 11]),
            Allocation(group_id=50, room_ids=[6], day=3, slots=[12, 13]),
            Allocation(group_id=51, room_ids=[3], day=3, slots=[14, 15]),
            Allocation(group_id=52, room_ids=[8], day=2, slots=[14, 15]),
            Allocation(group_id=53, room_ids=[1], day=2, slots=[12, 13]),
            Allocation(group_id=54, room_ids=[6], day=4, slots=[12, 13]),
            Allocation(group_id=55, room_ids=[1], day=4, slots=[14, 15]),
            Allocation(group_id=56, room_ids=[3], day=1, slots=[14, 15]),
            Allocation(group_id=57, room_ids=[25], day=1, slots=[14, 15]),
            Allocation(group_id=58, room_ids=[13], day=1, slots=[12, 13]),
            Allocation(group_id=59, room_ids=[10], day=4, slots=[10, 11]),
            Allocation(group_id=60, room_ids=[14], day=3, slots=[12, 13]),
            Allocation(group_id=61, room_ids=[16], day=1, slots=[12, 13]),
            Allocation(group_id=62, room_ids=[16], day=3, slots=[12, 13]),
            Allocation(group_id=63, room_ids=[5], day=4, slots=[10, 11]),
            Allocation(group_id=64, room_ids=[10], day=4, slots=[12, 13]),
            Allocation(group_id=65, room_ids=[13, 2], day=4, slots=[8]),
            Allocation(group_id=66, room_ids=[11, 3], day=4, slots=[8, 9]),
            Allocation(group_id=67, room_ids=[30], day=1, slots=[12, 13]),
            Allocation(group_id=68, room_ids=[14], day=1, slots=[10, 11]),
            Allocation(group_id=69, room_ids=[14], day=4, slots=[12, 13]),
            Allocation(group_id=70, room_ids=[3], day=2, slots=[14, 15]),
            Allocation(group_id=71, room_ids=[13], day=2, slots=[12, 13]),
            Allocation(group_id=72, room_ids=[15], day=4, slots=[14, 15]),
            Allocation(group_id=73, room_ids=[11], day=4, slots=[14, 15]),
            Allocation(group_id=74, room_ids=[13], day=4, slots=[12, 13]),
            Allocation(group_id=75, room_ids=[], day=3, slots=[10, 11]),
            Allocation(group_id=76, room_ids=[], day=3, slots=[8, 9]),
        ]
        msg = prob.check()
        # print(msg)
        self.assertNotEqual(msg, [])
