from __future__ import annotations

import argparse

from queue_client import QueueClient


class Minion(QueueClient):
    def run(self) -> None:
        self.connect()
        assert self.task_queue is not None
        assert self.result_queue is not None

        print("[minion] connected, waiting for tasks...")
        while True:
            task = self.task_queue.get()  # blocking
            if task is None:
                print("[minion] received stop signal, exiting.")
                break

            # Task from TP1: must have .work()
            task.work()
            self.result_queue.put(task)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    parser.add_argument("--authkey", default="secret")
    args = parser.parse_args()

    Minion(host=args.host, port=args.port, authkey=args.authkey).run()


if __name__ == "__main__":
    main()
