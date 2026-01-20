from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from task import Task


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/task":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")

        # Rebuild Task from JSON (TP3)
        task = Task.from_json(body)
        task.work()

        resp = task.to_json().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, fmt: str, *args) -> None:
        # less noisy logs
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    httpd = HTTPServer((args.host, args.port), Handler)
    print(f"[proxy] listening on http://{args.host}:{args.port}")
    print("[proxy] POST /task  (body = Task JSON)")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
