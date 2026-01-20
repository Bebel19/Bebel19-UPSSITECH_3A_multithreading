from __future__ import annotations

import argparse
from multiprocessing.managers import BaseManager
from queue import Queue


# These queues live in the manager process (server-side).
_task_queue: Queue = Queue()
_result_queue: Queue = Queue()


class QueueManager(BaseManager):
    """Server-side manager: exposes task_queue and result_queue."""

    pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    parser.add_argument("--authkey", default="secret")
    args = parser.parse_args()

    # Register server-side callables that return the actual objects.
    QueueManager.register("get_task_queue", callable=lambda: _task_queue)
    QueueManager.register("get_result_queue", callable=lambda: _result_queue)

    mgr = QueueManager(address=(args.host, args.port), authkey=args.authkey.encode())
    print(f"[manager] serving on {args.host}:{args.port}")
    mgr.get_server().serve_forever()


if __name__ == "__main__":
    main()
