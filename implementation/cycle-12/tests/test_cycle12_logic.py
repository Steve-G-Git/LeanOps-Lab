#!/usr/bin/env python3

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile


BASE = Path(__file__).parent


def load_module(name: str, filename: str):
    loader = SourceFileLoader(name, str(BASE / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


processor = load_module("processor", "leanops-health-event-processor")
notifier = load_module("notifier", "leanops-health-notifier")


def condition(severity: str, message: str) -> dict:
    return {
        "condition_id": processor.identify_condition(message),
        "severity": severity,
        "message": message,
    }


def empty_condition_state() -> dict:
    return {"version": 1, "active_conditions": {}}


def empty_notification_state() -> dict:
    return {"version": 1, "pending": {}, "notified_conditions": {}}


def run_observation(condition_state: dict, notification_state: dict, items: list):
    events, evidence_due = processor.update_condition_state(
        condition_state,
        items,
    )
    queue_events = processor.queue_notifications(notification_state, events)
    return events, evidence_due, queue_events


def test_warning_threshold_and_suppression():
    condition_state = empty_condition_state()
    notification_state = empty_notification_state()
    update = condition(
        "WARN",
        "2 package updates available in the current APT cache",
    )

    for occurrence in range(1, 4):
        _, evidence_due, queue_events = run_observation(
            condition_state,
            notification_state,
            [update],
        )
        assert not evidence_due
        assert not queue_events
        assert not notification_state["pending"]
        assert condition_state["active_conditions"]["package_updates"][
            "consecutive_count"
        ] == occurrence

    _, evidence_due, queue_events = run_observation(
        condition_state,
        notification_state,
        [update],
    )
    assert len(evidence_due) == 1
    assert len(queue_events) == 1
    assert notification_state["pending"]["package_updates"][
        "notification_type"
    ] == "ALERT"

    _, evidence_due, queue_events = run_observation(
        condition_state,
        notification_state,
        [update],
    )
    assert len(evidence_due) == 1  # evidence flag is set after collector success
    assert not queue_events
    assert len(notification_state["pending"]) == 1


def test_failure_is_immediate_and_distinct_conditions_group():
    condition_state = empty_condition_state()
    notification_state = empty_notification_state()
    items = [
        condition("FAIL", "SSH is not active"),
        condition("FAIL", "DNS resolution failed"),
    ]
    _, evidence_due, queue_events = run_observation(
        condition_state,
        notification_state,
        items,
    )
    assert len(evidence_due) == 2
    assert len(queue_events) == 2
    assert set(notification_state["pending"]) == {
        "ssh_inactive",
        "dns_resolution_failed",
    }

    message = notifier.build_message(
        list(notification_state["pending"].values()),
        "test@example.invalid",
    )
    body = message.get_content()
    assert "Conditions in this message: 2" in body
    assert "Condition ID: ssh_inactive" in body
    assert "Condition ID: dns_resolution_failed" in body


def test_existing_over_threshold_warning_is_queued_once():
    condition_state = empty_condition_state()
    condition_state["active_conditions"]["package_updates"] = {
        "severity": "WARN",
        "consecutive_count": 19,
        "first_seen": "2026-01-01T00:00:00Z",
        "last_seen": "2026-01-01T01:00:00Z",
        "last_message": "2 package updates available in the current APT cache",
        "evidence_collected": True,
    }
    notification_state = empty_notification_state()
    update = condition(
        "WARN",
        "2 package updates available in the current APT cache",
    )

    _, _, queue_events = run_observation(
        condition_state,
        notification_state,
        [update],
    )
    assert len(queue_events) == 1
    sent_items = list(notification_state["pending"].values())
    notifier.mark_sent(notification_state, sent_items)

    _, _, queue_events = run_observation(
        condition_state,
        notification_state,
        [update],
    )
    assert not queue_events
    assert not notification_state["pending"]


def test_recovery_after_sent_alert():
    condition_state = empty_condition_state()
    notification_state = empty_notification_state()
    failure = condition("FAIL", "SSH is not active")
    run_observation(condition_state, notification_state, [failure])
    sent_items = list(notification_state["pending"].values())
    notifier.mark_sent(notification_state, sent_items)
    assert "ssh_inactive" in notification_state["notified_conditions"]

    _, _, queue_events = run_observation(
        condition_state,
        notification_state,
        [],
    )
    assert len(queue_events) == 1
    assert notification_state["pending"]["ssh_inactive"][
        "notification_type"
    ] == "RECOVERY"


def test_unsent_alert_and_recovery_coalesce():
    condition_state = empty_condition_state()
    notification_state = empty_notification_state()
    failure = condition("FAIL", "SSH is not active")
    run_observation(condition_state, notification_state, [failure])
    assert notification_state["pending"]["ssh_inactive"][
        "notification_type"
    ] == "ALERT"

    _, _, queue_events = run_observation(
        condition_state,
        notification_state,
        [],
    )
    assert len(queue_events) == 1
    assert notification_state["pending"]["ssh_inactive"][
        "notification_type"
    ] == "ALERT_RECOVERED"


def test_delivery_failure_retains_pending_and_success_clears_it():
    original_state_path = notifier.NOTIFICATION_STATE_PATH
    original_log_path = notifier.NOTIFICATION_LOG_PATH
    original_config_path = notifier.SMTP_CONFIG_PATH
    original_send = notifier.send_message
    original_argv = notifier.sys.argv

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        notifier.NOTIFICATION_STATE_PATH = root / "notification-state.json"
        notifier.NOTIFICATION_LOG_PATH = root / "notification-events.tsv"
        notifier.SMTP_CONFIG_PATH = root / "smtp.conf"
        notifier.SMTP_CONFIG_PATH.write_text(
            "from test@example.invalid\n",
            encoding="utf-8",
        )

        state = empty_notification_state()
        state["pending"]["ssh_inactive"] = {
            "condition_id": "ssh_inactive",
            "notification_type": "ALERT",
            "severity": "FAIL",
            "message": "SSH is not active",
            "consecutive_count": 1,
            "first_seen": "2026-01-01T00:00:00Z",
            "last_seen": "2026-01-01T00:00:00Z",
            "evidence_collected": True,
            "queued_at": "2026-01-01T00:00:00Z",
        }
        notifier.NOTIFICATION_STATE_PATH.write_text(
            json.dumps(state),
            encoding="utf-8",
        )
        notifier.sys.argv = ["leanops-health-notifier"]

        def fail_send(message, recipient):
            raise RuntimeError("controlled SMTP failure")

        notifier.send_message = fail_send
        assert notifier.main() == 3
        retained = json.loads(
            notifier.NOTIFICATION_STATE_PATH.read_text(encoding="utf-8")
        )
        assert "ssh_inactive" in retained["pending"]
        assert "SEND_FAILED" in notifier.NOTIFICATION_LOG_PATH.read_text(
            encoding="utf-8"
        )

        notifier.send_message = lambda message, recipient: None
        assert notifier.main() == 0
        delivered = json.loads(
            notifier.NOTIFICATION_STATE_PATH.read_text(encoding="utf-8")
        )
        assert not delivered["pending"]
        assert "ssh_inactive" in delivered["notified_conditions"]

    notifier.NOTIFICATION_STATE_PATH = original_state_path
    notifier.NOTIFICATION_LOG_PATH = original_log_path
    notifier.SMTP_CONFIG_PATH = original_config_path
    notifier.send_message = original_send
    notifier.sys.argv = original_argv


def main():
    tests = [
        test_warning_threshold_and_suppression,
        test_failure_is_immediate_and_distinct_conditions_group,
        test_existing_over_threshold_warning_is_queued_once,
        test_recovery_after_sent_alert,
        test_unsent_alert_and_recovery_coalesce,
        test_delivery_failure_retains_pending_and_success_clears_it,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")


if __name__ == "__main__":
    main()
