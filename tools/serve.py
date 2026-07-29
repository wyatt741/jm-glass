#!/usr/bin/env python3
"""Preview server. HTTP/1.1 + threads on purpose: the project sheet requests 54
images at once and a single-threaded HTTP/1.0 server resets connections under
that, which looks exactly like broken images (PLAYBOOK §12 / KICKOFF step 7)."""
import functools
import http.server
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


class H(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(H, directory=str(ROOT))
    print(f"serving {ROOT} on http://127.0.0.1:{port}", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
