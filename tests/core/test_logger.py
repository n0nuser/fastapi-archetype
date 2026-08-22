"""Unit tests for logging configuration."""

import json
import logging
from collections.abc import Iterator
from typing import Any

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.core import logger as logger_module
from src.core.logger import setup_logging


@pytest.fixture
def reset_root_logger() -> Iterator[None]:
    yield
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)


@pytest.mark.usefixtures("reset_root_logger")
def test_json_format_emits_parseable_records(
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(logger_module.settings, "LOG_FORMAT", "json")

    setup_logging()
    logging.getLogger("test.json").info("structured hello")

    lines = [line for line in capsys.readouterr().err.splitlines() if line.strip()]
    payload: dict[str, Any] = json.loads(lines[-1])

    assert payload["message"] == "structured hello"
    assert payload["level"] == "INFO"
    assert payload["name"] == "test.json"
    assert "timestamp" in payload
    assert "correlation_id" in payload


@pytest.mark.usefixtures("reset_root_logger")
def test_text_format_keeps_plain_lines(
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(logger_module.settings, "LOG_FORMAT", "text")

    setup_logging()
    logging.getLogger("test.text").info("plain hello")

    err = capsys.readouterr().err
    last_line = [line for line in err.splitlines() if line.strip()][-1]

    assert "plain hello" in last_line
    with pytest.raises(json.JSONDecodeError):
        json.loads(last_line)
