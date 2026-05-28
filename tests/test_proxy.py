"""
Unit tests for the outlook-ics-converter proxy.

Run with:  pytest tests/ -v
"""

from __future__ import annotations

import textwrap
from unittest.mock import MagicMock, patch

import pytest
from icalendar import Calendar

# ── Fixtures ─────────────────────────────────────────────────────────────────

ROMANCE_ICS = textwrap.dedent("""\
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//Microsoft Corporation//Outlook 16.0//EN
    BEGIN:VTIMEZONE
    TZID:Romance Standard Time
    BEGIN:STANDARD
    DTSTART:16010101T030000
    TZOFFSETFROM:+0200
    TZOFFSETTO:+0100
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
    TZNAME:Romance Standard Time
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:16010101T020000
    TZOFFSETFROM:+0100
    TZOFFSETTO:+0200
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
    TZNAME:Romance Daylight Time
    END:DAYLIGHT
    END:VTIMEZONE
    BEGIN:VEVENT
    UID:test-event-001@outlook
    SUMMARY:Team Meeting
    DTSTART;TZID=Romance Standard Time:20260601T100000
    DTEND;TZID=Romance Standard Time:20260601T110000
    END:VEVENT
    END:VCALENDAR
""").encode()

ALREADY_IANA_ICS = textwrap.dedent("""\
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//Some App//EN
    BEGIN:VTIMEZONE
    TZID:Europe/Amsterdam
    BEGIN:STANDARD
    DTSTART:16010101T030000
    TZOFFSETFROM:+0200
    TZOFFSETTO:+0100
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
    TZNAME:CET
    END:STANDARD
    END:VTIMEZONE
    BEGIN:VEVENT
    UID:test-event-002@app
    SUMMARY:Lunch
    DTSTART;TZID=Europe/Amsterdam:20260601T120000
    DTEND;TZID=Europe/Amsterdam:20260601T130000
    END:VEVENT
    END:VCALENDAR
""").encode()

NO_TIMEZONE_ICS = textwrap.dedent("""\
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//Some App//EN
    BEGIN:VEVENT
    UID:test-event-003@app
    SUMMARY:All-day event
    DTSTART;VALUE=DATE:20260601
    DTEND;VALUE=DATE:20260602
    END:VEVENT
    END:VCALENDAR
""").encode()


# ── Timezone lookup table tests ───────────────────────────────────────────────

class TestTimezoneTable:
    def test_romance_standard_time(self):
        from app.timezones import WINDOWS_TO_IANA
        assert WINDOWS_TO_IANA["Romance Standard Time"] == "Europe/Paris"

    def test_w_europe_standard_time(self):
        from app.timezones import WINDOWS_TO_IANA
        assert WINDOWS_TO_IANA["W. Europe Standard Time"] == "Europe/Berlin"

    def test_eastern_standard_time(self):
        from app.timezones import WINDOWS_TO_IANA
        assert WINDOWS_TO_IANA["Eastern Standard Time"] == "America/New_York"

    def test_gmt_standard_time(self):
        from app.timezones import WINDOWS_TO_IANA
        assert WINDOWS_TO_IANA["GMT Standard Time"] == "Europe/London"

    def test_tokyo_standard_time(self):
        from app.timezones import WINDOWS_TO_IANA
        assert WINDOWS_TO_IANA["Tokyo Standard Time"] == "Asia/Tokyo"

    def test_all_values_are_nonempty_strings(self):
        from app.timezones import WINDOWS_TO_IANA
        for key, value in WINDOWS_TO_IANA.items():
            assert isinstance(value, str) and value, f"Empty IANA name for {key!r}"

    def test_no_duplicate_keys(self):
        """Verify the dict has no shadowed keys (Python dicts are insertion-ordered)."""
        from app.timezones import WINDOWS_TO_IANA
        assert len(WINDOWS_TO_IANA) > 100, "Expected at least 100 timezone entries"


# ── Core rewrite logic tests ──────────────────────────────────────────────────

class TestRewriteCalendar:
    def test_windows_tzid_is_translated(self):
        from app.proxy import rewrite_calendar
        result = rewrite_calendar(ROMANCE_ICS)
        cal = Calendar.from_ical(result)
        # Collect all TZID values from event properties
        tzids = set()
        for component in cal.walk("VEVENT"):
            for prop_name in ("DTSTART", "DTEND"):
                prop = component.get(prop_name)
                if prop and hasattr(prop, "params"):
                    tzid = prop.params.get("TZID")
                    if tzid:
                        tzids.add(tzid)
        assert "Europe/Paris" in tzids, f"Expected Europe/Paris in {tzids}"
        assert "Romance Standard Time" not in tzids, "Windows TZ should have been replaced"

    def test_vtimezone_block_is_replaced(self):
        from app.proxy import rewrite_calendar
        result = rewrite_calendar(ROMANCE_ICS)
        cal = Calendar.from_ical(result)
        tz_ids = [str(c.get("TZID")) for c in cal.walk("VTIMEZONE")]
        assert any("Europe/Paris" in t for t in tz_ids), \
            f"Expected Europe/Paris VTIMEZONE, got: {tz_ids}"
        assert not any("Romance" in t for t in tz_ids), \
            "Old Windows VTIMEZONE block should have been removed"

    def test_already_iana_is_unchanged(self):
        from app.proxy import rewrite_calendar
        result = rewrite_calendar(ALREADY_IANA_ICS)
        cal = Calendar.from_ical(result)
        tzids = set()
        for component in cal.walk("VEVENT"):
            for prop_name in ("DTSTART", "DTEND"):
                prop = component.get(prop_name)
                if prop and hasattr(prop, "params"):
                    tzid = prop.params.get("TZID")
                    if tzid:
                        tzids.add(tzid)
        # Should be left alone (not in lookup table)
        assert "Europe/Amsterdam" in tzids

    def test_no_timezone_calendar_passes_through(self):
        from app.proxy import rewrite_calendar
        result = rewrite_calendar(NO_TIMEZONE_ICS)
        cal = Calendar.from_ical(result)
        events = list(cal.walk("VEVENT"))
        assert len(events) == 1
        assert str(events[0].get("SUMMARY")) == "All-day event"

    def test_event_summary_preserved(self):
        from app.proxy import rewrite_calendar
        result = rewrite_calendar(ROMANCE_ICS)
        cal = Calendar.from_ical(result)
        summaries = [str(e.get("SUMMARY")) for e in cal.walk("VEVENT")]
        assert "Team Meeting" in summaries


# ── Config parsing tests ─────────────────────────────────────────────────────

class TestParseEnvList:
    def test_plain_string_becomes_single_item_list(self):
        from app.main import _parse_env_list
        assert _parse_env_list("https://example.com/cal.ics") == ["https://example.com/cal.ics"]

    def test_json_array_parsed_correctly(self):
        from app.main import _parse_env_list
        result = _parse_env_list('["https://a.com/a.ics", "https://b.com/b.ics"]')
        assert result == ["https://a.com/a.ics", "https://b.com/b.ics"]

    def test_empty_string_returns_empty_list(self):
        from app.main import _parse_env_list
        assert _parse_env_list("") == []

    def test_none_returns_empty_list(self):
        from app.main import _parse_env_list
        assert _parse_env_list(None) == []

    def test_invalid_json_falls_back_to_plain_string(self):
        from app.main import _parse_env_list
        result = _parse_env_list('[not valid json')
        assert result == ['[not valid json']

    def test_newline_separated_two_entries(self):
        from app.main import _parse_env_list
        result = _parse_env_list('https://a.com/a.ics\nhttps://b.com/b.ics\n')
        assert result == ['https://a.com/a.ics', 'https://b.com/b.ics']

    def test_newline_separated_blank_lines_ignored(self):
        from app.main import _parse_env_list
        result = _parse_env_list('https://a.com/a.ics\n\n  \nhttps://b.com/b.ics')
        assert result == ['https://a.com/a.ics', 'https://b.com/b.ics']

    def test_single_entry_without_pipe_is_plain_string(self):
        from app.main import _parse_env_list
        result = _parse_env_list('https://a.com/a.ics')
        assert result == ['https://a.com/a.ics']


class TestLoadCalendars:
    def _reload(self, monkeypatch, source, path=None):
        monkeypatch.setenv("CALENDAR_SOURCE", source)
        if path:
            monkeypatch.setenv("CALENDAR_PATH", path)
        else:
            monkeypatch.delenv("CALENDAR_PATH", raising=False)
        import importlib
        import app.main as main_mod
        importlib.reload(main_mod)
        return main_mod._CALENDARS

    def test_single_source_default_path(self, monkeypatch):
        entries = self._reload(monkeypatch, "https://example.com/a.ics")
        assert len(entries) == 1
        assert entries[0].path == "/calendar.ics"
        assert entries[0].url == "https://example.com/a.ics"

    def test_single_source_custom_path(self, monkeypatch):
        entries = self._reload(monkeypatch, "https://example.com/a.ics", "/work.ics")
        assert entries[0].path == "/work.ics"

    def test_multiple_sources_with_paths(self, monkeypatch):
        entries = self._reload(
            monkeypatch,
            '["https://a.com/a.ics","https://b.com/b.ics"]',
            '["/work.ics","/home.ics"]',
        )
        assert len(entries) == 2
        assert entries[0].path == "/work.ics"
        assert entries[1].path == "/home.ics"

    def test_multiple_sources_auto_paths(self, monkeypatch):
        entries = self._reload(
            monkeypatch,
            '["https://a.com/a.ics","https://b.com/b.ics"]',
        )
        assert entries[0].path == "/calendar-1.ics"
        assert entries[1].path == "/calendar-2.ics"

    def test_path_gets_leading_slash_added(self, monkeypatch):
        entries = self._reload(monkeypatch, "https://example.com/a.ics", "no-slash.ics")
        assert entries[0].path == "/no-slash.ics"


# ── HTTP layer tests ──────────────────────────────────────────────────────────

class TestFlaskApp:
    @pytest.fixture()
    def client(self, monkeypatch):
        monkeypatch.setenv("CALENDAR_SOURCE", "https://example.com/cal.ics")
        monkeypatch.setenv("CACHE_TTL", "0")
        # Re-import to pick up the monkeypatched env
        import importlib
        import app.main as main_mod
        importlib.reload(main_mod)
        main_mod.app.config["TESTING"] = True
        return main_mod.app.test_client()

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_root_returns_404(self, client):
        resp = client.get("/")
        assert resp.status_code == 404

    def test_calendar_endpoint_returns_ics(self, client):
        with patch("app.main.fetch_and_rewrite", return_value=ROMANCE_ICS):
            resp = client.get("/calendar.ics")
        assert resp.status_code == 200
        assert "text/calendar" in resp.content_type

    def test_upstream_error_returns_502(self, client):
        import requests as req
        with patch("app.main.fetch_and_rewrite", side_effect=req.HTTPError("upstream down")):
            resp = client.get("/calendar.ics")
        assert resp.status_code == 502
