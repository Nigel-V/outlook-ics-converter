"""
Flask application for the Outlook ICS timezone proxy.

Calendar feeds are configured via environment variables — no upstream URLs
are ever exposed to the end user.

CALENDAR_SOURCE and CALENDAR_PATH each accept either a plain string (single
calendar) or a JSON array (multiple calendars). Entries are paired by index;
if fewer paths than sources are given the remaining paths are auto-generated.

Examples
--------
Single calendar:
    CALENDAR_SOURCE=https://outlook.office365.com/owa/.../calendar.ics
    CALENDAR_PATH=/my-calendar.ics          # optional, default: /calendar.ics

Multiple calendars:
    CALENDAR_SOURCE='["https://.../work.ics","https://.../personal.ics"]'
    CALENDAR_PATH='["/work.ics","/personal.ics"]'

Other settings
--------------
PROXY_REQUEST_TIMEOUT   Seconds to wait for upstream fetch         (default: 30)
CACHE_TTL               Cache lifetime in seconds; 0 = disabled    (default: 300)
PORT                    Port to listen on                           (default: 8080)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

from flask import Flask, Response, jsonify

from .proxy import fetch_and_rewrite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

PROXY_REQUEST_TIMEOUT: int = int(os.environ.get("PROXY_REQUEST_TIMEOUT", "30"))
CACHE_TTL: int = int(os.environ.get("CACHE_TTL", "300"))


def _parse_env_list(value: str | None) -> list[str]:
    """
    Parse an environment variable that may be a plain string, a newline-separated
    block (YAML block scalar with |), or a JSON array.

    Returns a list of non-empty stripped strings.

    Plain string      → ["value"]
    Newline-separated → each non-empty line as an element
    JSON array        → each element as a string
    Empty / unset     → []
    """
    if not value:
        return []
    value = value.strip()

    # JSON array
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            logger.warning("Could not parse %r as a JSON array — treating as plain text", value)

    # Newline-separated (YAML block scalar)
    if "\n" in value:
        return [line.strip() for line in value.splitlines() if line.strip()]

    # Plain string (single value)
    return [value]


@dataclass
class CalendarEntry:
    """A single configured upstream calendar feed."""
    path: str        # URL path the proxy serves this feed at (e.g. /my-cal.ics)
    url: str         # Upstream Outlook ICS URL
    _cache_body: Optional[bytes] = field(default=None, repr=False)
    _cache_ts: float = field(default=0.0, repr=False)

    def get(self) -> bytes:
        """Return (possibly cached) rewritten ICS bytes."""
        now = time.monotonic()
        if CACHE_TTL > 0 and self._cache_body is not None:
            if now - self._cache_ts < CACHE_TTL:
                logger.debug("Cache hit for %s", self.path)
                return self._cache_body

        body = fetch_and_rewrite(self.url, timeout=PROXY_REQUEST_TIMEOUT)

        if CACHE_TTL > 0:
            self._cache_body = body
            self._cache_ts = now

        return body


def _load_calendars() -> list[CalendarEntry]:
    """
    Build the list of CalendarEntry objects from environment variables.

    CALENDAR_SOURCE and CALENDAR_PATH are each parsed as either a plain string
    or a JSON array. Sources and paths are paired by index. If there are fewer
    paths than sources the remaining entries receive auto-generated paths
    (/calendar.ics for a single source, /calendar-N.ics for multiple).
    """
    sources = _parse_env_list(os.environ.get("CALENDAR_SOURCE"))
    paths   = _parse_env_list(os.environ.get("CALENDAR_PATH"))

    entries: list[CalendarEntry] = []
    for i, url in enumerate(sources):
        if i < len(paths):
            path = paths[i]
        elif len(sources) == 1:
            path = "/calendar.ics"
        else:
            path = f"/calendar-{i + 1}.ics"

        if not path.startswith("/"):
            path = "/" + path
        entries.append(CalendarEntry(path=path, url=url))

    return entries


_CALENDARS: list[CalendarEntry] = _load_calendars()

# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def _make_handler(entry: CalendarEntry):
    """Return a view function bound to *entry*."""
    def handler():
        try:
            body = entry.get()
        except Exception as exc:
            logger.exception("Error proxying %s: %s", entry.path, exc)
            return Response(
                f"Failed to fetch or process the upstream calendar: {exc}",
                status=502,
                mimetype="text/plain",
            )
        return Response(
            body,
            status=200,
            mimetype="text/calendar; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{entry.path.lstrip("/")}"',
                "Cache-Control": f"public, max-age={CACHE_TTL}" if CACHE_TTL > 0 else "no-store",
            },
        )
    # Flask requires unique endpoint names
    handler.__name__ = f"calendar_{entry.path.replace('/', '_').strip('_')}"
    return handler


for _entry in _CALENDARS:
    app.add_url_rule(_entry.path, view_func=_make_handler(_entry))
    logger.info("Registered route %s → %s", _entry.path, _entry.url[:60] + "…" if len(_entry.url) > 60 else _entry.url)

if not _CALENDARS:
    logger.warning(
        "No calendars configured. Set CALENDAR_SOURCE (and optionally "
        "CALENDAR_PATH) environment variables to activate the proxy."
    )

# ---------------------------------------------------------------------------
# Utility routes
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    """Health check endpoint for Docker / load-balancer probes."""
    return jsonify({"status": "ok", "calendars": len(_CALENDARS)})



# ---------------------------------------------------------------------------
# Entry point (development only — use gunicorn in production / Docker)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)
