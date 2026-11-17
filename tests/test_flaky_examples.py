"""
tests/test_flaky_examples.py

These four tests are DELIBERATELY flaky — not bugs in app code, but
illustrations of what real flakiness looks like, so Smart Tests' flaky-test
detection has something genuine to identify. They are intentionally kept
separate from app/auth.py, app/config.py, and app/notifications.py so they
never interfere with this repo's three deterministic root-cause clusters
(auth, config, notifications) — flakiness here is its own, orthogonal
signal: noise, not a real regression.

Each test fails at a different, predictable rate across many runs, even
though any single run's outcome is genuinely random:

  test_flaky_pure_chance            ~50% fail rate - a coin flip, the
                                     simplest possible flaky test.
  test_flaky_simulated_latency       ~50% fail rate - looks like it's
                                     testing a latency SLA, but the "latency"
                                     is just a random draw, so the assertion
                                     is exactly as flaky as a coin flip
                                     wearing a disguise. This is a very
                                     common real-world flaky pattern.
  test_flaky_race_condition_style    ~10% fail rate - two independent random
                                     signals that are supposed to agree;
                                     occasionally, by chance, they don't -
                                     similar to real race-condition bugs
                                     where two async operations sometimes
                                     resolve in the wrong order.
  test_flaky_eventual_consistency    ~40% fail rate - a read-after-write
                                     that polls a replica only three times.
                                     The replica's lag is a random 0-4
                                     ticks, so a lag of 3 or 4 still looks
                                     stale when the retry budget runs out.
                                     Same shape as a real eventually
                                     consistent lookup whose retries are
                                     a little too short.
"""
import random
import time


def test_flaky_pure_chance():
    assert random.random() > 0.5


def test_flaky_simulated_latency():
    simulated_latency = random.uniform(0.0, 0.02)
    time.sleep(simulated_latency)
    assert simulated_latency < 0.01  # "SLA" that holds only half the time


def test_flaky_race_condition_style():
    signal_a = random.random()
    signal_b = random.random()
    assert abs(signal_a - signal_b) > 0.05


def test_flaky_eventual_consistency():
    # Replica lag is 0-4 ticks, uniform. Three polls catch up only when
    # the lag was 0, 1, or 2, so this fails 2 times out of 5.
    replica_lag_ticks = random.randint(0, 4)
    observed = "stale"
    for _ in range(3):
        if replica_lag_ticks == 0:
            observed = "committed"
            break
        replica_lag_ticks -= 1
    assert observed == "committed"
