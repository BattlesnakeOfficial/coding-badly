import json
import os
import unittest

from parameterized import parameterized

import battlesnake


class MoveTestCases(unittest.TestCase):
    def test_sanity(self):
        self.assertTrue(True)

    @parameterized.expand(os.listdir("src/tests"))
    def test_move(self, filepath):
        self.assertTrue(filepath.endswith(".move"))
        with open(os.path.join("src/tests", filepath), "r") as f:
            test_data = f.readlines()

        settings = json.loads(test_data[0])
        request = json.loads(test_data[1])

        move = battlesnake.Battlesnake().move(request)
        self.assertIn(move, settings["acceptedMoves"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
