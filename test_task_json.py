import unittest

from task import Task


class TestTaskJson(unittest.TestCase):
    def test_roundtrip_json(self) -> None:
        a = Task()
        txt = a.to_json()
        b = Task.from_json(txt)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
