# outlook-ics-converter

A lightweight Docker proxy that translates proprietary Microsoft Outlook/Windows timezone names (e.g. `Romance Standard Time`) into standard IANA timezone identifiers (e.g. `Europe/Paris`) before serving `.ics` calendar feeds to clients like Google Calendar and Apple Calendar.

## Why this exists

Outlook embeds Windows-specific timezone names in published `.ics` feeds. These names are not understood by most calendar clients, which can cause events to render at the wrong time or fail to import entirely. This proxy sits transparently between Outlook and any subscribing calendar client and rewrites the feed on-the-fly.

## Quick start

```yaml
# docker-compose.yml
services:
  proxy:
    image: ghcr.io/youruser/outlook-ics-converter:latest
    ports:
      - "8080:8080"
    environment:
      CALENDAR_SOURCE: "https://outlook.office365.com/owa/calendar/.../calendar.ics"
```

```bash
docker compose up -d
```

Subscribe your calendar client to `http://localhost:8080/calendar.ics`.

## Configuration

All configuration is done via environment variables. Upstream URLs are never exposed to end users.

`CALENDAR_SOURCE` and `CALENDAR_PATH` each accept either a **plain string** (single calendar), a **JSON array** (multiple calendars), or a **newline-separated block** (multiple calendars, ideal for Docker Compose). Entries are paired by index.

### Single calendar

```bash
CALENDAR_SOURCE=https://outlook.office365.com/owa/calendar/.../calendar.ics
CALENDAR_PATH=/my-calendar.ics      # optional — default: /calendar.ics
```

### Multiple calendars 

```yaml
environment:
  CALENDAR_SOURCE: |
    https://outlook.office365.com/.../work.ics
    https://outlook.office365.com/.../personal.ics
  CALENDAR_PATH: |
    /work.ics
    /personal.ics
```

If `CALENDAR_PATH` has fewer entries than `CALENDAR_SOURCE`, the remaining paths are generated automatically (`/calendar-1.ics`, `/calendar-2.ics`, …).


> [!TIP]
> If you care enough about privacy to host a private proxy, it is strongly recommended to use a random string as the `CALENDAR_PATH` variable to prevent casual discovery of your calendar feeds.

### Tuning

| Variable | Default | Description |
|---|---|---|
| `CACHE_TTL` | `300` | Cache lifetime in seconds (`0` = disabled) |
| `PROXY_REQUEST_TIMEOUT` | `30` | Upstream fetch timeout in seconds |
| `PORT` | `8080` | Listening port (development server only) |

## Endpoints

| Endpoint | Description |
|---|---|
| `/{CALENDAR_PATH}.ics` | Proxied, timezone-corrected feed (path configurable) |
| `/health` | Health check — returns `{"status":"ok"}` |

## How it works

1. Fetches the upstream `.ics` feed on each request (with caching).
2. Parses the calendar using the [icalendar](https://github.com/collective/icalendar) library.
3. Translates every Windows `TZID` string to a standard IANA name using the [Unicode CLDR `windowsZones` mapping](https://github.com/unicode-org/cldr/blob/main/common/supplemental/windowsZones.xml).
4. Replaces `VTIMEZONE` blocks with RFC 5545-compliant definitions.
5. Returns the corrected feed with `Content-Type: text/calendar`.

## Development

```bash
pip install -r requirements.txt
CALENDAR_SOURCE="https://..." python -m app.main
```

### Running tests

```bash
pip install pytest
pytest tests/ -v
```

### Building the Docker image

```bash
docker compose build
docker compose up
curl http://localhost:8080/health
```

## Timezone mapping

The mapping table lives in [`app/timezones.py`](app/timezones.py) and covers all ~140 Windows timezone names sourced from Unicode CLDR. If you find a missing entry, please open a pull request.
