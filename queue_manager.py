# queue_manager.py
from __future__ import annotations

import argparse
from multiprocessing.managers import BaseManager
from queue import Queue

_task_queue: Queue = Queue()
_result_queue: Queue = Queue()

class QueueManager(BaseManager):
    """Server-side manager: exposes task_queue and result_queue."""
    pass


def start_manager(host: str = "127.0.0.1", port: int = 50000, authkey: bytes = b"secret") -> None:
    """Start the manager server (blocking, serve_forever)."""
    global _task_queue, _result_queue
    # Fresh queues each time the manager starts
    _task_queue = Queue()
    _result_queue = Queue()

    QueueManager.register("get_task_queue", callable=lambda: _task_queue)
    QueueManager.register("get_result_queue", callable=lambda: _result_queue)

    mgr = QueueManager(address=(host, port), authkey=authkey)
    print(f"[manager] serving on {host}:{port}")
    mgr.get_server().serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    parser.add_argument("--authkey", default="secret")
    args = parser.parse_args()

    start_manager(args.host, args.port, args.authkey.encode())


if __name__ == "__main__":
    main()
