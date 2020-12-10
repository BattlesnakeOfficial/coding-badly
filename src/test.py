import os
import unittest


class MoveTestCases(unittest.TestCase):
    def test_sanity(self):
        self.assertTrue(True)

    def test_moves(self):
        for filepath in os.listdir("src/tests"):
            if not filepath.endswith(".move"):
                continue
            with open(os.path.join("src/tests", filepath), "r") as f:
                test_data = f.readlines()

            test_name = "TODO"
            with self.subTest(name=test_name, file=filepath):
                # self.assertEqual(test_data, "barf")
                self.assertTrue(True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
