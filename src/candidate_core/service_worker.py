"""Loopback health service used to prove ownership without a product UI."""

from __future__ import annotations

import argparse
import socketserver
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class HealthServer(ThreadingHTTPServer):
    def server_bind(self) -> None:
        socketserver.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = str(host)
        self.server_port = int(port)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            body = b'{"status":"ok"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="productctl-service")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port-file", required=True)
    args = parser.parse_args(argv)
    sys.stderr.write("worker starting\n")
    sys.stderr.flush()
    server = HealthServer((args.bind, 0), HealthHandler)
    port = server.server_address[1]
    port_path = Path(args.port_file)
    port_path.write_text(str(port) + "\n", encoding="utf-8")
    sys.stderr.write(f"listening {args.bind}:{port}\n")
    sys.stderr.flush()
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
