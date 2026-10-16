#!/usr/bin/env python3
"""Loopback-only static preview server with room for parallel browser checks."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class PreviewServer(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True


class PreviewHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep successful image/font requests from flooding CI and terminal logs.
        if len(args) > 1 and str(args[1]).startswith(('4', '5')):
            super().log_message(format, *args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    handler = partial(PreviewHandler, directory=str(Path(__file__).resolve().parents[1]))
    with PreviewServer(('127.0.0.1', args.port), handler) as server:
        print(f'FLYLYFE preview: http://127.0.0.1:{args.port}', flush=True)
        server.serve_forever()
