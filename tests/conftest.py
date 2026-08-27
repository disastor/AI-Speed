"""
tests/conftest.py

Simulates realistic test durations for demo purposes ONLY. Controlled
entirely by environment variables so the suite still runs near-instantly
during normal development or quick local iteration, and only becomes
"slow" when explicitly asked to for the live demo.

  DEMO_TEST_DELAY_SECONDS       - base delay added to every test (with
                                   jitter so it doesn't look robotic).
                                   Default: 0 (no delay).
  DEMO_SLOW_TEST_EXTRA_SECONDS  - additional delay added ONLY to tests
                                   marked @pytest.mark.slow, on top of the
                                   base delay above. Default: 0.

Neither variable changes what a test actually checks — only how long it
takes to run. This exists purely to make a 55+-test suite feel like a
real, non-trivial CI run for demo purposes, and to give Smart Tests' Predictive
Test Selection something meaningful to save time on.
"""
import os
import random
import time

import pytest

BASE_DELAY = float(os.environ.get("DEMO_TEST_DELAY_SECONDS", "0"))
SLOW_EXTRA_DELAY = float(os.environ.get("DEMO_SLOW_TEST_EXTRA_SECONDS", "0"))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks a test as long-running (demo purposes only)"
    )


@pytest.fixture(autouse=True)
def _simulate_realistic_duration(request):
    if BASE_DELAY > 0:
        # +/- 40% jitter so 55 tests don't look suspiciously identical
        time.sleep(BASE_DELAY * random.uniform(0.6, 1.4))

    if SLOW_EXTRA_DELAY > 0 and request.node.get_closest_marker("slow"):
        time.sleep(SLOW_EXTRA_DELAY)

    yield
