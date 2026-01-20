from __future__ import annotations

from multiprocessing.managers import BaseManager
from typing import Any


class QueueManager(BaseManager):
    """Client-side manager class (same name, no callables here)."""
    pass


class QueueClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 50000, authkey: str = "secret"):
        self.host = host
        self.port = port
        self.authkey = authkey

        self.task_queue: Any = None
        self.result_queue: Any = None

    def connect(self) -> None:
        # Client registers the exposed methods (NO callable on client side)
        QueueManager.register("get_task_queue")
        QueueManager.register("get_result_queue")

        mgr = QueueManager(address=(self.host, self.port), authkey=self.authkey.encode())
        mgr.connect()

        self.task_queue = mgr.get_task_queue()
        self.result_queue = mgr.get_result_queue()
