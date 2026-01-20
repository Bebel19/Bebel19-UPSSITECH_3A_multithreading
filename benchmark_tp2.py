from __future__ import annotations

import argparse
import statistics
import time
import socket
from dataclasses import dataclass
from multiprocessing import Process
from typing import List, Dict, Any

from boss import Boss
from minion import Minion
from queue_manager import start_manager


def get_free_port() -> int:
    """Ask OS for a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@dataclass
class RunResult:
    minions: int
    tasks: int
    size: int
    step: int
    wall_s: float
    task_times_s: List[float]

    @property
    def throughput(self) -> float:
        return self.tasks / self.wall_s if self.wall_s > 0 else float("inf")

    @property
    def sum_task_time(self) -> float:
        return float(sum(self.task_times_s))

    @property
    def max_task_time(self) -> float:
        return float(max(self.task_times_s)) if self.task_times_s else 0.0

    @property
    def mean_task_time(self) -> float:
        return float(statistics.mean(self.task_times_s)) if self.task_times_s else 0.0


def run_once(
    minions: int, tasks: int, size: int, step: int, authkey: str = "secret"
) -> RunResult:
    host = "127.0.0.1"
    port = get_free_port()

    # 1) Start manager (separate process)
    mgr_proc = Process(
        target=start_manager, args=(host, port, authkey.encode()), daemon=True
    )
    mgr_proc.start()
    time.sleep(0.25)  # small delay to let server start

    # 2) Start minions
    minion_procs: List[Process] = []
    for _ in range(minions):
        p = Process(
            target=Minion(host=host, port=port, authkey=authkey).run, daemon=True
        )
        p.start()
        minion_procs.append(p)

    time.sleep(0.25)  # let minions connect

    # 3) Run boss in this process (so we can time it and get results directly)
    sizes = [size + i * step for i in range(tasks)]
    boss = Boss(host=host, port=port, authkey=authkey)

    t0 = time.perf_counter()
    results = boss.run(sizes=sizes, n_minions=minions)
    wall = time.perf_counter() - t0

    # 4) Wait for minions to exit (boss sent None sentinels)
    for p in minion_procs:
        p.join(timeout=5)

    # 5) Stop manager (it serves_forever -> terminate)
    if mgr_proc.is_alive():
        mgr_proc.terminate()
        mgr_proc.join(timeout=2)

    # Extract per-task times
    task_times = []
    for t in results:
        task_times.append(float(getattr(t, "time", 0.0)))

    return RunResult(
        minions=minions,
        tasks=tasks,
        size=size,
        step=step,
        wall_s=float(wall),
        task_times_s=task_times,
    )


def aggregate(results: List[RunResult]) -> Dict[str, Any]:
    walls = [r.wall_s for r in results]
    thr = [r.throughput for r in results]
    return {
        "wall_mean": statistics.mean(walls),
        "wall_stdev": statistics.pstdev(walls) if len(walls) > 1 else 0.0,
        "throughput_mean": statistics.mean(thr),
        "throughput_stdev": statistics.pstdev(thr) if len(thr) > 1 else 0.0,
        "task_mean_mean": statistics.mean([r.mean_task_time for r in results]),
        "task_max_mean": statistics.mean([r.max_task_time for r in results]),
        "sum_task_time_mean": statistics.mean([r.sum_task_time for r in results]),
    }


def print_table(rows: List[Dict[str, Any]]) -> None:
    headers = [
        "minions",
        "tasks",
        "size",
        "step",
        "repeats",
        "wall_mean(s)",
        "wall_sd",
        "throughput(task/s)",
        "throughput_sd",
        "mean_task_time(s)",
        "max_task_time(s)",
        "sum_task_time(s)",
    ]
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * len(headers)) + "|")

    for r in rows:
        print(
            "| {minions} | {tasks} | {size} | {step} | {repeats} | "
            "{wall_mean:.6f} | {wall_sd:.6f} | "
            "{thr_mean:.3f} | {thr_sd:.3f} | "
            "{task_mean_mean:.6f} | {task_max_mean:.6f} | {sum_task_time_mean:.6f} |".format(
                minions=r["minions"],
                tasks=r["tasks"],
                size=r["size"],
                step=r["step"],
                repeats=r["repeats"],
                wall_mean=r["wall_mean"],
                wall_sd=r["wall_stdev"],
                thr_mean=r["throughput_mean"],
                thr_sd=r["throughput_stdev"],
                task_mean_mean=r["task_mean_mean"],
                task_max_mean=r["task_max_mean"],
                sum_task_time_mean=r["sum_task_time_mean"],
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark TP2 Boss/Minions configs.")
    parser.add_argument(
        "--minions",
        type=int,
        nargs="+",
        default=[1, 2, 4],
        help="List of minion counts to try",
    )
    parser.add_argument("--tasks", type=int, default=10)
    parser.add_argument("--size", type=int, default=300)
    parser.add_argument("--step", type=int, default=50)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    rows: List[Dict[str, Any]] = []

    for m in args.minions:
        runs: List[RunResult] = []
        for i in range(args.repeats):
            r = run_once(minions=m, tasks=args.tasks, size=args.size, step=args.step)
            runs.append(r)
            print(
                f"[run] minions={m} repeat={i + 1}/{args.repeats} wall={r.wall_s:.4f}s throughput={r.throughput:.2f} task/s"
            )

        agg = aggregate(runs)
        rows.append(
            {
                "minions": m,
                "tasks": args.tasks,
                "size": args.size,
                "step": args.step,
                "repeats": args.repeats,
                **agg,
            }
        )

    print("\n### Summary (Markdown table)\n")
    print_table(rows)


if __name__ == "__main__":
    main()
