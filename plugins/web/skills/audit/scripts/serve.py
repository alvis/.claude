"""Minimal HTTP file server for audit scripts. Stdlib only."""

import http.server
import os
import random
import sys


def main():
    directory = os.path.dirname(os.path.abspath(__file__))
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=directory, **kwargs
    )

    for _ in range(10):
        port = random.randint(49152, 65535)
        try:
            server = http.server.HTTPServer(("127.0.0.1", port), handler)
        except OSError:
            continue
        print(f"SERVING_PORT:{port}", flush=True)
        server.serve_forever()

    print("Failed to bind after 10 attempts", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
