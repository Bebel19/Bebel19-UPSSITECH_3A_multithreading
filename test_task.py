import unittest

import numpy as np
from task import Task


class TestTask(unittest.TestCase):
    def test_task_solves_linear_system(self):
        t = Task(identifier=1, size=50)  # petit -> test rapide
        t.work()
        np.testing.assert_allclose(t.a @ t.x, t.b, rtol=1e-7, atol=0)


if __name__ == "__main__":
    unittest.main()
