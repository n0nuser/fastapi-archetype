"""Unit tests for OpenTelemetry configuration."""

from _pytest.monkeypatch import MonkeyPatch
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from src.app import configure_tracing


def test_configure_tracing_installs_sdk_provider(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    configure_tracing()

    assert isinstance(trace.get_tracer_provider(), TracerProvider)
