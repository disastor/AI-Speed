"""
Minimal stand-in test runner used ONLY to validate this demo repo's failure
math locally, since this sandbox has no network access to `pip install
pytest`. The real repo's tests/ files are genuine pytest tests and should be
run with real pytest in Dana's actual CI. This script fakes just enough of
pytest's surface (pytest.raises, a monkeypatch fixture) to execute the same
test functions and report pass/fail/error counts and clusters.
"""
import importlib
import sys
import traceback
from contextlib import contextmanager

sys.path.insert(0, ".")


class _Raises:
    def __init__(self, exc_type):
        self.exc_type = exc_type
        self.raised = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"DID NOT RAISE {self.exc_type}")
        if not issubclass(exc_type, self.exc_type):
            return False
        self.raised = True
        return True


class _FakePytestModule:
    @staticmethod
    def raises(exc_type):
        return _Raises(exc_type)


class _MonkeyPatch:
    def __init__(self):
        self._saved = []

    def setattr(self, obj, name, value):
        self._saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, value)

    def undo(self):
        for obj, name, val in reversed(self._saved):
            setattr(obj, name, val)


sys.modules["pytest"] = _FakePytestModule()

TEST_MODULES = [
    "tests.test_auth",
    "tests.test_payments",
    "tests.test_orders",
    "tests.test_users",
    "tests.test_notifications",
]


def run():
    results = {}
    total_pass = total_fail = 0
    for modname in TEST_MODULES:
        if modname in sys.modules:
            del sys.modules[modname]
        # also reload app modules fresh each file to avoid cross-contamination
        for m in ["app.auth", "app.config", "app.payments", "app.orders", "app.users", "app.notifications", "app"]:
            if m in sys.modules:
                del sys.modules[m]

        mod = importlib.import_module(modname)
        test_fns = [getattr(mod, n) for n in dir(mod) if n.startswith("test_")]
        file_results = []
        for fn in test_fns:
            mp = _MonkeyPatch()
            args = []
            if "monkeypatch" in fn.__code__.co_varnames[: fn.__code__.co_argcount]:
                args.append(mp)
            try:
                fn(*args)
                file_results.append((fn.__name__, "PASS", None))
                total_pass += 1
            except Exception as e:
                file_results.append((fn.__name__, "FAIL", f"{type(e).__name__}: {e}"))
                total_fail += 1
            finally:
                mp.undo()
        results[modname] = file_results

    print(f"\n{'='*60}")
    for modname, file_results in results.items():
        fails = [r for r in file_results if r[1] == "FAIL"]
        print(f"\n{modname}: {len(file_results) - len(fails)} passed, {len(fails)} failed")
        for name, status, err in file_results:
            if status == "FAIL":
                print(f"  FAIL {name} -> {err}")
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_pass} passed, {total_fail} failed out of {total_pass + total_fail}")


if __name__ == "__main__":
    run()
