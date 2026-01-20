from __future__ import annotations

import argparse
from typing import List

from queue_client import QueueClient
from task import Task  # from TP1


class Boss(QueueClient):
    def run(self, sizes: List[int], n_minions: int) -> List[Task]:
        self.connect()
        assert self.task_queue is not None
        assert self.result_queue is not None

        tasks = [Task(size=s, identifier=i) for i, s in enumerate(sizes)]

        print(f"[boss] sending {len(tasks)} tasks...")
        for t in tasks:
            self.task_queue.put(t)

        results: List[Task] = []
        print("[boss] collecting results...")
        for _ in range(len(tasks)):
            done = self.result_queue.get()  # blocking
            results.append(done)

        print("[boss] stopping minions...")
        for _ in range(n_minions):
            self.task_queue.put(None)

        return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    parser.add_argument("--authkey", default="secret")
    parser.add_argument("--minions", type=int, default=2)
    parser.add_argument("--tasks", type=int, default=10)
    parser.add_argument("--size", type=int, default=300)  # base matrix size
    parser.add_argument("--step", type=int, default=50)  # size increment
    args = parser.parse_args()

    sizes = [args.size + i * args.step for i in range(args.tasks)]
    results = Boss(host=args.host, port=args.port, authkey=args.authkey).run(
        sizes, args.minions
    )

    # Print a small summary
    for t in sorted(results, key=lambda x: x.identifier):
        # Task from TP1 typically stores timing in t.time
        print(
            f"[boss] task id={t.identifier} size={t.size} time={getattr(t, 'time', None)}"
        )


if __name__ == "__main__":
    main()
