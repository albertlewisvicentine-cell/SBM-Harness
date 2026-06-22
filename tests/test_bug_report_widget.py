"""Tests for bug_report_widget: ContextCollector, HistoryStore, BugReportWidget."""

from __future__ import annotations

import platform
from unittest.mock import patch

import pytest

from bug_report_widget import (
    BugReportWidget,
    ContextCollector,
    HistoryStore,
    _CONSOLE_ERROR_BUFFER,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clear_errors():
    """Reset the module-level console-error buffer between tests."""
    BugReportWidget.clear_console_errors()


# ---------------------------------------------------------------------------
# ContextCollector
# ---------------------------------------------------------------------------


class TestContextCollector:
    def setup_method(self):
        _clear_errors()

    def test_url_extracted_from_request_url_env(self):
        with patch.dict("os.environ", {"REQUEST_URL": "https://example.com/page"}):
            ctx = ContextCollector()
        assert ctx.url == "https://example.com/page"

    def test_url_falls_back_to_url_env(self):
        env = {"URL": "https://fallback.example.com"}
        with patch.dict("os.environ", env, clear=True):
            ctx = ContextCollector()
        assert ctx.url == "https://fallback.example.com"

    def test_url_empty_when_no_env_var_set(self):
        with patch.dict("os.environ", {}, clear=True):
            ctx = ContextCollector()
        assert ctx.url == ""

    def test_session_flags_contains_user_key(self):
        with patch.dict("os.environ", {"USER": "alice", "HOME": "/home/alice"}):
            ctx = ContextCollector()
        assert ctx.session_flags.get("USER") == "alice"
        assert ctx.session_flags.get("HOME") == "/home/alice"

    def test_session_flags_excludes_unrelated_keys(self):
        with patch.dict("os.environ", {"MY_RANDOM_VAR": "xyz"}):
            ctx = ContextCollector()
        assert "MY_RANDOM_VAR" not in ctx.session_flags

    def test_hardware_env_contains_platform_fields(self):
        ctx = ContextCollector()
        assert "PLATFORM_SYSTEM" in ctx.hardware_env
        assert ctx.hardware_env["PLATFORM_SYSTEM"] == platform.uname().system

    def test_hardware_env_picks_up_cpu_prefix(self):
        with patch.dict("os.environ", {"CPU_COUNT": "8"}):
            ctx = ContextCollector()
        assert ctx.hardware_env.get("CPU_COUNT") == "8"

    def test_console_errors_empty_when_buffer_clear(self):
        ctx = ContextCollector()
        assert ctx.console_errors == []

    def test_console_errors_captures_last_three(self):
        for msg in ("err1", "err2", "err3", "err4"):
            BugReportWidget.record_console_error(msg)
        ctx = ContextCollector()
        assert ctx.console_errors == ["err2", "err3", "err4"]

    def test_console_errors_fewer_than_three(self):
        BugReportWidget.record_console_error("only-error")
        ctx = ContextCollector()
        assert ctx.console_errors == ["only-error"]

    def test_to_dict_returns_all_keys(self):
        ctx = ContextCollector()
        d = ctx.to_dict()
        assert set(d.keys()) == {"url", "session_flags", "hardware_env", "console_errors"}

    def test_to_dict_values_are_copies(self):
        ctx = ContextCollector()
        d = ctx.to_dict()
        d["console_errors"].append("injected")
        assert "injected" not in ctx.console_errors


# ---------------------------------------------------------------------------
# HistoryStore
# ---------------------------------------------------------------------------


class TestHistoryStore:
    def test_best_value_none_for_empty_store(self):
        store = HistoryStore()
        assert store.best_value_for("title") is None

    def test_record_and_retrieve(self):
        store = HistoryStore()
        store.record({"title": "Login crash", "severity": "high"})
        assert store.best_value_for("title") == "Login crash"
        assert store.best_value_for("severity") == "high"

    def test_most_recent_value_returned(self):
        store = HistoryStore()
        store.record({"title": "First"})
        store.record({"title": "Second"})
        assert store.best_value_for("title") == "Second"

    def test_duplicate_value_moved_to_most_recent(self):
        store = HistoryStore()
        store.record({"component": "auth"})
        store.record({"component": "ui"})
        store.record({"component": "auth"})
        assert store.best_value_for("component") == "auth"

    def test_none_values_not_stored(self):
        store = HistoryStore()
        store.record({"title": None})
        assert store.best_value_for("title") is None

    def test_autofill_replaces_none_only(self):
        store = HistoryStore()
        store.record({"title": "Old title", "severity": "low"})
        result = store.autofill({"title": None, "severity": "critical", "reporter": None})
        assert result["title"] == "Old title"
        assert result["severity"] == "critical"  # explicit value preserved
        assert result["reporter"] is None  # no history → stays None

    def test_autofill_returns_new_dict(self):
        store = HistoryStore()
        original = {"title": None}
        result = store.autofill(original)
        original["title"] = "mutated"
        assert result["title"] is None  # result is independent

    def test_clear_removes_all_history(self):
        store = HistoryStore()
        store.record({"title": "something"})
        store.clear()
        assert store.best_value_for("title") is None


# ---------------------------------------------------------------------------
# BugReportWidget
# ---------------------------------------------------------------------------


class TestBugReportWidget:
    def setup_method(self):
        _clear_errors()

    def test_default_fields_present_after_init(self):
        widget = BugReportWidget()
        for field in ("title", "description", "component", "severity", "reporter"):
            assert field in widget.fields

    def test_caller_fields_override_defaults(self):
        widget = BugReportWidget({"title": "My Bug", "severity": "high"})
        assert widget.fields["title"] == "My Bug"
        assert widget.fields["severity"] == "high"

    def test_none_fields_autofilled_from_history(self):
        store = HistoryStore()
        store.record({"title": "Historic bug", "reporter": "bob"})
        widget = BugReportWidget(history_store=store)
        assert widget.fields["title"] == "Historic bug"
        assert widget.fields["reporter"] == "bob"

    def test_explicit_value_not_overwritten_by_history(self):
        store = HistoryStore()
        store.record({"title": "Old title"})
        widget = BugReportWidget({"title": "New title"}, history_store=store)
        assert widget.fields["title"] == "New title"

    def test_context_attached_on_init(self):
        widget = BugReportWidget()
        assert isinstance(widget.context, ContextCollector)

    def test_update_field_mutates_fields(self):
        widget = BugReportWidget()
        widget.update_field("severity", "critical")
        assert widget.fields["severity"] == "critical"

    def test_submit_returns_fields_and_context(self):
        widget = BugReportWidget({"title": "Submit test"})
        report = widget.submit()
        assert "fields" in report
        assert "context" in report
        assert report["fields"]["title"] == "Submit test"

    def test_submit_persists_values_to_history(self):
        store = HistoryStore()
        widget = BugReportWidget({"title": "Persisted"}, history_store=store)
        widget.submit()
        assert store.best_value_for("title") == "Persisted"

    def test_submit_extra_fields_merged(self):
        widget = BugReportWidget()
        report = widget.submit({"build_id": "42"})
        assert report["fields"]["build_id"] == "42"

    def test_submit_extra_fields_persisted_to_history(self):
        store = HistoryStore()
        widget = BugReportWidget(history_store=store)
        widget.submit({"build_id": "99"})
        assert store.best_value_for("build_id") == "99"

    def test_submit_none_values_not_persisted(self):
        store = HistoryStore()
        widget = BugReportWidget(history_store=store)
        widget.submit()
        # All defaults are None → nothing should be in history
        assert store.best_value_for("title") is None

    def test_shared_history_store_across_instances(self):
        store = HistoryStore()
        first = BugReportWidget({"title": "Shared report", "reporter": "alice"}, history_store=store)
        first.submit()
        second = BugReportWidget(history_store=store)
        assert second.fields["title"] == "Shared report"
        assert second.fields["reporter"] == "alice"

    def test_context_includes_console_errors(self):
        BugReportWidget.record_console_error("TypeError: x is undefined")
        widget = BugReportWidget()
        assert "TypeError: x is undefined" in widget.context.console_errors

    def test_clear_console_errors_flushes_buffer(self):
        BugReportWidget.record_console_error("err")
        BugReportWidget.clear_console_errors()
        widget = BugReportWidget()
        assert widget.context.console_errors == []

    def test_context_url_captured_from_env(self):
        with patch.dict("os.environ", {"REQUEST_URL": "https://app.local/report"}):
            widget = BugReportWidget()
        assert widget.context.url == "https://app.local/report"

    def test_independent_history_when_no_store_provided(self):
        w1 = BugReportWidget({"title": "Widget1"})
        w1.submit()
        w2 = BugReportWidget()
        # w2 has its own fresh store, so no history bleed-through
        assert w2.fields["title"] is None
