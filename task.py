import time

import numpy as np

import json
from typing import Any


class Task:
    def __init__(self, identifier=0, size=None):
        self.identifier = identifier
        # choosee the size of the problem
        self.size = size or np.random.randint(300, 3_000)
        # Generate the input of the problem
        self.a = np.random.rand(self.size, self.size)
        self.b = np.random.rand(self.size)
        # prepare room for the results
        self.x = np.zeros((self.size))
        self.time = 0

    def work(self):
        start = time.perf_counter()
        self.x = np.linalg.solve(self.a, self.b)
        self.time = time.perf_counter() - start

    def to_json(self) -> str:
        """Serialize the task to a JSON string (C++/Python friendly)."""
        payload: dict[str, Any] = {
            "identifier": self.identifier,
            "size": self.size,
            "time": self.time,
            # numpy arrays -> lists so JSON can encode them
            "a": self.a.tolist() if self.a is not None else None,
            "b": self.b.tolist() if self.b is not None else None,
            "x": self.x.tolist() if self.x is not None else None,
        }
        return json.dumps(payload)

    @staticmethod
    def from_json(text: str) -> "Task":
        """Deserialize a task from a JSON string."""
        data = json.loads(text)

        t = Task(size=data.get("size"), identifier=data.get("identifier"))
        t.time = data.get("time")

        # lists -> numpy arrays
        t.a = np.array(data["a"]) if data.get("a") is not None else None
        t.b = np.array(data["b"]) if data.get("b") is not None else None
        t.x = np.array(data["x"]) if data.get("x") is not None else None

        return t

    def __eq__(self, other: "Task") -> bool:
        if not isinstance(other, Task):
            return False

        def arr_eq(u, v) -> bool:
            if u is None and v is None:
                return True
            if (u is None) != (v is None):
                return False
            return bool(np.array_equal(u, v))

        # time can be float -> allow small tolerance
        time_ok = (self.time is None and other.time is None) or (
            self.time is not None
            and other.time is not None
            and abs(self.time - other.time) < 1e-12
        )

        return (
            self.identifier == other.identifier
            and self.size == other.size
            and time_ok
            and arr_eq(self.a, other.a)
            and arr_eq(self.b, other.b)
            and arr_eq(self.x, other.x)
        )
