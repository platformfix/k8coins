# Adapted from jpetazzo/container.training's dockercoins/rng/rng.py
# (Apache 2.0). See NOTICE.
from flask import Flask, Response
import os
import socket
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Enable debugging if the DEBUG environment variable is set and starts with Y
app.debug = os.environ.get("DEBUG", "").lower().startswith('y')

hostname = socket.gethostname()

urandom = os.open("/dev/urandom", os.O_RDONLY)

bytes_served = Counter(
    "k8coins_rng_bytes_served_total", "Total bytes of random data served")
requests_served = Counter(
    "k8coins_rng_requests_served_total", "Total requests served")


@app.route("/")
def index():
    return "RNG running on {}\n".format(hostname)


@app.route("/healthz")
def healthz():
    # rng has no external dependencies once /dev/urandom is open, so it is
    # healthy whenever the process is up and answering requests at all.
    return "ok\n"


@app.route("/live")
def live():
    return "ok\n"


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.route("/<int:how_many_bytes>")
def rng(how_many_bytes):
    # Simulate a little bit of delay
    time.sleep(0.1)
    data = os.read(urandom, how_many_bytes)
    bytes_served.inc(len(data))
    requests_served.inc()
    return Response(data, content_type="application/octet-stream")


if __name__ == "__main__":
    app.run(port=80)
