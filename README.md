# Build at AI Speed — Demo Runbook

A small Python app + pytest suite built to run on CBCI and be triaged by
CloudBees Smart Tests, staged as two acts that pay off the "AI agent pushed
code it shouldn't have" customer story:

- **Act 1 — Governance (CBCI):** an AI-authored PR touching `app/auth.py`
  (a sensitive path) is stopped by a pipeline gate and requires named human
  approval before it can proceed. A second AI-authored PR touching
  `app/config.py` (not sensitive) sails through ungated — governance is
  surgical, not a blanket slowdown.
- **Act 2 — Triage & Speed (Smart Tests):** a `nightly` branch simulates
  several overnight AI PRs landing together. The suite goes red — 30 of 55
  tests fail. Smart Tests' failure clustering shows those 30 failures trace
  back to exactly **3** root causes, not 30 unrelated problems. Then a fix
  commit demonstrates Predictive Test Selection: instead of re-running all
  55 tests, only the relevant subset runs.

Verified locally: this repo's baseline is 55 tests, all green. With all
three simulated AI PRs merged (the `nightly` scenario), 30 fail across 3
distinct root causes — see "What actually happens," below, for the exact
breakdown.

## Prerequisites

- A GitHub repo you control, with this code pushed to `main`.
- CBCI multibranch pipeline (or GitHub Organization folder) pointed at that
  repo, so `feature/*` and `nightly` branches are auto-discovered.
- A Jenkins agent with Python 3 available. `smart-tests` itself needs
  **Python 3.13+** (unless you install it via `uv`, which sidesteps that
  requirement) and **Java 8+** on the agent — Jenkins agents almost always
  already have Java, but confirm the Python version before the demo.
- A CloudBees Smart Tests workspace/API key, stored as a Jenkins Secret
  Text credential named `smart-tests-token` (matches the `Jenkinsfile`).
- If you want the real Unify gate instead of the `input`-step stand-in
  below: wire that in and simplify the "Governance Gate" stage accordingly.
  As built, the gate uses a plain Jenkins `input` step guarded by a
  path-check script — real, demonstrable, and doesn't borrow capability
  from a product you're not showing on screen.

## One-time setup

```bash
# from this directory
git init
git add .
git commit -m "Baseline: Build at AI Speed demo app"
git remote add origin <your-github-repo-url>
git push -u origin main

# now build the branches used in the demo
./scripts/create_demo_branches.sh origin
git push origin feature/ai-agent-config-tuning
git push origin feature/ai-agent-auth-refactor
git push origin nightly
```

In CBCI: point a Multibranch Pipeline at the repo. It should pick up
`main`, both `feature/*` branches, and `nightly` automatically (each has
its own `Jenkinsfile`-driven build).

Configure the `input` step's approver: edit `Jenkinsfile`, replace
`platform-team` with a real user/group in your Jenkins instance so the
approval prompt has a name behind it on screen.

## What actually happens (verified numbers)

| Scenario | Branch | Sensitive path touched? | Gate fires? | Tests run | Failures |
|---|---|---|---|---|---|
| Baseline | `main` | — | No | 55 | 0 |
| AI PR #1 | `feature/ai-agent-config-tuning` | No | **No** | subset | some (config-related) |
| AI PR #2 | `feature/ai-agent-auth-refactor` | **Yes** (`app/auth.py`) | **Yes** | subset | some (auth-related) |
| Nightly (all merged) | `nightly` | Yes | Yes | 55 (full) | **30**, in **3 clusters** |

The three clusters, verified by running the suite locally against each
patch:

1. **Auth signature check inverted** (`app/auth.py`) — 16 failures across
   `test_auth.py`, `test_payments.py`, `test_users.py`, all surfacing as
   `ValueError: invalid signature` (or a tampered token now silently
   passing — a real security regression, useful to call out).
2. **Config defaults zeroed out** (`app/config.py`) — 9 failures, all in
   `test_orders.py`, surfacing as `OrderError: invalid db timeout
   configured` / `max_retries must be at least 1`.
3. **Notification template renamed** (`app/notifications.py`) — 5
   failures, all in `test_notifications.py`, surfacing as `KeyError:
   'unknown template: welcome'`.

That's the "47 failures, are there really 47 problems" beat — just with
real numbers (30 and 3) instead of the placeholder ones from the pitch.
If you want to hit exactly 47, pad `test_orders.py` or
`test_notifications.py` with a few more assertions per cluster; the ratio
matters more than the absolute count.

## Live demo script

**Act 1 — Governance (~3 min)**

1. Open GitHub, show `feature/ai-agent-config-tuning` — narrate it as an
   AI coding assistant's overnight PR.
2. Trigger/show the CBCI build for that branch: gate stage logs "No
   sensitive paths touched," pipeline proceeds without stopping.
3. Open `feature/ai-agent-auth-refactor` — same framing, but this one
   touches `auth.py`.
4. Show the CBCI build pause at the `input` step: "Approve change to
   authentication/payment logic?" Approve it live, narrating that this is
   recorded in the build's own history — audit trail, not a side system.
5. Callback line: "This is the same gap the CISO in Customer X's story
   had — the difference is it's closed without migrating off Jenkins."

**Act 2 — Triage & Speed (~4 min)**

1. Merge/trigger the `nightly` branch build — the full suite runs, goes
   red: 30 of 55 failing.
2. In the Smart Tests UI, open the failure clustering view for that build
   — show the 30 failures rolling up into 3 groups.
3. Narrate each cluster in one line using the table above (auth, config,
   notifications) — "Dana's team doesn't read 30 stack traces, they read
   3."
4. Push a fix (revert `auth.py` to the version in `main`) and re-run.
   Show Predictive Test Selection choosing a small subset instead of the
   full 55 — land on the time-saved number Smart Tests reports for that
   run.

## Files

```
app/                  the demo application (auth, config, payments, orders, users, notifications)
tests/                pytest suite, 55 tests, all green on main
branch-patches/       the three "AI agent" bugs, one per file, applied by create_demo_branches.sh
scripts/
  check_sensitive_paths.sh   the governance gate's policy check
  create_demo_branches.sh    builds feature/* and nightly branches from main
  mini_runner.py             stdlib-only test runner used to verify failure counts in a
                              sandbox without network access — not needed once you have
                              real pytest; safe to delete before you ship this to the team
Jenkinsfile           the pipeline: gate stage + Smart Tests record/subset/run stages
```
