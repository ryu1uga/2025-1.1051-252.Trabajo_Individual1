# ids/ids_worker.py
import json
import os
import time
import redis
from collections import defaultdict

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
r = redis.from_url(REDIS_URL, decode_responses=True)

# simple in-memory counters (sliding window naive)
ip_counters = defaultdict(lambda: [])
ADMIN_AUTH_FAIL_WINDOW = 30  # seconds
ADMIN_AUTH_FAIL_THRESHOLD = 5
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_THRESHOLD = 100  # req per minute

pubsub = r.pubsub()
pubsub.subscribe('events')

def now_ts():
    return int(time.time())

def prune_list(lst, window):
    cutoff = now_ts() - window
    while lst and lst[0] < cutoff:
        lst.pop(0)

print("IDS worker started, waiting for events...")
for message in pubsub.listen():
    if message['type'] != 'message': 
        continue
    try:
        evt = json.loads(message['data'])
    except Exception as e:
        print("bad evt", e); continue

    # Common processing
    ip = evt.get('client_ip', 'unknown')
    t = now_ts()

    # rate counting
    ip_counters[ip].append(t)
    prune_list(ip_counters[ip], RATE_LIMIT_WINDOW)
    if len(ip_counters[ip]) > RATE_LIMIT_THRESHOLD:
        # alert: high rate
        print(f"[ALERT] High rate from {ip}: {len(ip_counters[ip])} reqs in last {RATE_LIMIT_WINDOW}s")
        # here -> call webhook or push to alert queue

    # canary hit
    if evt.get('type') == 'canary' or '/.canary/' in evt.get('path',''):
        print(f"[CRITICAL] Canary token accessed by {ip} path={evt.get('path')}")
        # escalate immediately (e.g., webhook, block ip)

    # repeated admin auth failures
    if evt.get('type') == 'auth_fail' and evt.get('path','').startswith('/api/v1/admin'):
        # record timestamps in a simple list in redis for persistence
        key = f"fail:{ip}"
        r.rpush(key, t)
        r.expire(key, ADMIN_AUTH_FAIL_WINDOW)
        fails = r.lrange(key, 0, -1)
        if len(fails) >= ADMIN_AUTH_FAIL_THRESHOLD:
            print(f"[ALERT] {len(fails)} admin auth fails from {ip} in {ADMIN_AUTH_FAIL_WINDOW}s")
            # escalate