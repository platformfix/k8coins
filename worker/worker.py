# Adapted from jpetazzo/container.training's dockercoins/worker/worker.py
# (Apache 2.0). See NOTICE.
import logging
import os
import threading
from redis import Redis
import requests
import time
from flask import Flask, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

DEBUG = os.environ.get("DEBUG", "").lower().startswith("y")

log = logging.getLogger(__name__)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


redis = Redis("redis")

hashes_total = Counter("k8coins_hashes_total", "Total hash attempts made")
coins_total = Counter("k8coins_coins_total", "Total coins found")

# Updated after every unit of work that actually completes a round trip to
# rng and hasher. /healthz reads this to decide whether the loop is making
# real progress, not just whether the process happens to still be running.
last_progress = time.time()
HEALTHY_WITHIN_SECONDS = 30


def get_random_bytes():
    r = requests.get("http://rng/32")
    return r.content


def hash_bytes(data):
    r = requests.post("http://hasher/",
                      data=data,
                      headers={"Content-Type": "application/octet-stream"})
    hex_hash = r.text
    return hex_hash


def work_loop(interval=1):
    deadline = 0
    loops_done = 0
    while True:
        if time.time() > deadline:
            log.info("{} units of work done, updating hash counter"
                     .format(loops_done))
            redis.incrby("hashes", loops_done)
            loops_done = 0
            deadline = time.time() + interval
        work_once()
        loops_done += 1


def work_once():
    global last_progress
    log.debug("Doing one unit of work")
    time.sleep(0.1)
    random_bytes = get_random_bytes()
    hex_hash = hash_bytes(random_bytes)
    hashes_total.inc()
    last_progress = time.time()
    if not hex_hash.startswith('0'):
        log.debug("No coin found")
        return
    log.info("Coin found: {}...".format(hex_hash[:8]))
    created = redis.hset("wallet", hex_hash, random_bytes)
    if not created:
        log.info("We already had that coin")
    else:
        coins_total.inc()


# worker has no HTTP server otherwise; this exists purely so it can be
# probed and scraped like the other services, run on a background thread
# alongside the work loop.
metrics_app = Flask(__name__)


@metrics_app.route("/healthz")
def healthz():
    age = time.time() - last_progress
    if age > HEALTHY_WITHIN_SECONDS:
        return Response(
            "stalled: no progress in {:.0f}s\n".format(age), status=503)
    return "ok\n"


@metrics_app.route("/live")
def live():
    return "ok\n"


@metrics_app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


def run_metrics_server():
    metrics_app.run(host="0.0.0.0", port=80)


if __name__ == "__main__":
    threading.Thread(target=run_metrics_server, daemon=True).start()
    while True:
        try:
            work_loop()
        except:
            log.exception("In work loop:")
            log.error("Waiting 10s and restarting.")
            time.sleep(10)
