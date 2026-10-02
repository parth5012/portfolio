import json
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

NAME_MAX = 100
MESSAGE_MIN = 10
MESSAGE_MAX = 5000
EMAIL_MAX = 254
DELIVERY_TIMEOUT = 10

NAME_REQUIRED = "name is required"
EMAIL_REQUIRED = "email is required"
MESSAGE_REQUIRED = "message is required"
EMAIL_BAD = "that email address does not look right"
NAME_TOO_LONG = f"please keep your name under {NAME_MAX} characters"
MESSAGE_TOO_SHORT = f"please write at least {MESSAGE_MIN} characters"
MESSAGE_TOO_LONG = f"please keep it under {MESSAGE_MAX} characters"
UNREADABLE = "could not read that submission"
NOT_CONFIGURED = "the contact form is not switched on yet"
DELIVERY_FAILED = "that did not reach me, please email me directly"
THROTTLED = "too many messages from that address, try again later"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


class WebhookUnreachable(Exception):
    """The webhook could not be reached at all: DNS, TLS, timeout."""


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def validate(payload):
    if not isinstance(payload, dict):
        return None, [UNREADABLE]

    name = _text(payload.get("name"))
    email = _text(payload.get("email"))
    message = _text(payload.get("message"))
    errors = []

    if not name:
        errors.append(NAME_REQUIRED)
    elif len(name) > NAME_MAX:
        errors.append(NAME_TOO_LONG)

    if not email:
        errors.append(EMAIL_REQUIRED)
    elif len(email) > EMAIL_MAX or not EMAIL_RE.match(email):
        errors.append(EMAIL_BAD)

    if not message:
        errors.append(MESSAGE_REQUIRED)
    elif len(message) < MESSAGE_MIN:
        errors.append(MESSAGE_TOO_SHORT)
    elif len(message) > MESSAGE_MAX:
        errors.append(MESSAGE_TOO_LONG)

    if errors:
        return None, errors

    return {"name": name, "email": email, "message": message}, []


def is_honeypot(payload):
    """A real person never sees this field, so anything in it is a bot."""
    return bool(_text(payload.get("website")))


def deliver(url, payload, timeout=DELIVERY_TIMEOUT):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, socket.timeout, OSError) as exc:
        raise WebhookUnreachable(str(exc)) from exc


class RateLimiter:
    """Sliding window, kept in memory. Enough to stop a double-submit storm."""

    def __init__(self, limit=5, window_seconds=600):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits = {}
        self._lock = threading.Lock()

    def allow(self, key, limit=None):
        now = time.monotonic()
        cutoff = now - self.window_seconds
        cap = self.limit if limit is None else limit
        with self._lock:
            hits = deque(t for t in self._hits.get(key, ()) if t > cutoff)
            if len(hits) >= cap:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True

    def reset(self):
        with self._lock:
            self._hits.clear()


RATE_LIMITER = RateLimiter(
    # Generous on purpose: mobile carriers and office Wi-Fi put many real people
    # behind one address. This is here to stop a double-submit storm or a naive
    # script, not to ration genuine humans.
    limit=int(os.environ.get("CONTACT_RATE_LIMIT", 20)),
    window_seconds=int(os.environ.get("CONTACT_RATE_WINDOW", 3600)),
)

bp = Blueprint("contact", __name__)


@bp.post("/api/contact")
def submit():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "errors": [UNREADABLE]}), 400

    if is_honeypot(payload):
        # Answer exactly like a success so a bot learns nothing, send nothing.
        return jsonify({"ok": True}), 200

    limit = current_app.config.get("CONTACT_RATE_LIMIT", RATE_LIMITER.limit)
    if not RATE_LIMITER.allow(request.remote_addr or "unknown", limit=limit):
        return jsonify({"ok": False, "errors": [THROTTLED]}), 429

    cleaned, errors = validate(payload)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    webhook = current_app.config.get("CONTACT_WEBHOOK") or os.environ.get("CONTACT_WEBHOOK", "")
    if not webhook:
        current_app.logger.warning("contact form used but CONTACT_WEBHOOK is not set")
        return jsonify({"ok": False, "errors": [NOT_CONFIGURED]}), 503

    record = dict(cleaned)
    record["source"] = "parthchawla.dev"
    record["received_at"] = datetime.now(timezone.utc).isoformat()

    try:
        status = deliver(webhook, record, DELIVERY_TIMEOUT)
    except WebhookUnreachable:
        current_app.logger.exception("contact webhook unreachable")
        return jsonify({"ok": False, "errors": [DELIVERY_FAILED]}), 502

    if not 200 <= status < 300:
        current_app.logger.error("contact webhook returned %s", status)
        return jsonify({"ok": False, "errors": [DELIVERY_FAILED]}), 502

    return jsonify({"ok": True}), 200


def init_app(app):
    app.config.setdefault("CONTACT_WEBHOOK", os.environ.get("CONTACT_WEBHOOK", ""))
    app.config.setdefault("CONTACT_RATE_LIMIT", RATE_LIMITER.limit)
    app.register_blueprint(bp)