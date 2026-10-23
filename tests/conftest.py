"""Recorded-service tests: offline replay by default, `--live` to detect drift.

Adapted from the template of the `testing` skill, together with
vcr_support.py.  The tangled test modules (test_*.py) come from the .nw
files in src/kthutils; this file and vcr_support.py are plain files.
pyproject.toml blocks the network for replay (`addopts`).

The project adds two kinds of fixtures at the end of the file:

    isolation             the session (from the import of this file on) and
                          every test get their own typerconf configuration,
                          and tests see no STAYAWHILE_*/ONEDRIVE_* variables,
                          so the developer's own setup can neither change a
                          result nor be written to; code that reads the
                          configuration at import (`kthutils config`) shares
                          the session's file
    KTH sessions          `kth_session` builds a module's session from the
                          stored KTH credentials, or skips the test

Modes:

    pytest                                   replay committed cassettes, offline
    pytest --live                            run against the real service, re-record
                                             into a temp dir, compare shapes with the
                                             committed cassettes (values never shown)
    pytest --live --live-writes              also run tests marked `mutates`
    make -C tests live / live-writes / kth_live   the same through make
    pytest --record-mode=once -k test_new    record a new test's cassette
    pytest --record-mode=rewrite -k test_x   deliberately re-record after drift

Recording (any mode but replay) needs TEST_PSEUDONYM_KEY set to a secret
that stays out of the repo (e.g. in the keyring or a password manager).
Keep it stable: the same key gives the same pseudonyms, so re-recordings
produce small, reviewable diffs.

Markers:

    live                  needs the real service; skipped unless --live
    mutates               changes state on the service (POST, PUT, DELETE);
                          replayed normally, skipped under --live unless
                          --live-writes, and then only against a sandbox
    synthetic_text(*keys) these free-text fields hold synthetic sandbox prose;
                          record them verbatim instead of redacting them
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

import pytest

# Import the helper next to this file, also when tests/ is a package or
# pytest runs with --import-mode=importlib.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vcr_support  # noqa: E402

SERVICE_TOKEN_ENV = "STAYAWHILE_API_KEY"
# Read once, before the isolation fixtures below remove the variable from
# every test's environment.
LIVE_SERVICE_TOKEN = os.environ.get(SERVICE_TOKEN_ENV)
LIVE_MARKER_FILE = ".pytest-live-cassettes"  # only directories holding it are wiped
SCAN_ALLOW_FILE = "scan-allow.txt"  # known false positives of the leak scan


def record_mode_of(config):
    return config.getoption("--record-mode") or "none"


def pytest_addoption(parser):
    group = parser.getgroup("live", "live service checks")
    group.addoption("--live", action="store_true",
                    help="run recorded tests against the real service and "
                         "report cassette drift")
    group.addoption("--live-dir", default=None,
                    help="where --live writes fresh cassettes; give it as "
                         "--live-dir=PATH (default: a private directory under the temp dir)")
    group.addoption("--live-writes", action="store_true",
                    help="under --live, also run tests marked `mutates`")


def pytest_configure(config):
    for line in ("live: needs the real service; skipped unless --live",
                 "mutates: changes state on the service; skipped under --live "
                 "unless --live-writes",
                 "synthetic_text(*keys): record these free-text fields verbatim"):
        config.addinivalue_line("markers", line)
    config._recorded_dirs = set()
    if config.getoption("--live"):
        # Set the options themselves, not only the fixtures: the network
        # block of pytest-recording reads the options, and live tests
        # without a cassette must reach the service too.
        config.option.record_mode = "all"
        config.option.block_network = False
        root = Path(str(config.rootpath))
        tag = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:10]
        config._live_dir = Path(config.getoption("--live-dir") or vcr_support.private_dir()
                                / f"{root.name}-{tag}-live-cassettes").resolve()
        prepare_live_dir(config._live_dir, root.resolve())
    if record_mode_of(config) != "none" and not os.environ.get(vcr_support.KEY_ENV):
        pytest.exit(f"refusing to record: set {vcr_support.KEY_ENV} so that "
                    "personal data is pseudonymized", returncode=2)


def prepare_live_dir(live_dir: Path, root: Path):
    """Empty the live directory, but only one that an earlier live run made.

    A stale run must not mask drift, yet a mistyped --live-dir must never
    delete a project: refuse anything that is not empty and not ours.
    """
    if live_dir == root or live_dir in root.parents:
        pytest.exit(f"refusing --live-dir={live_dir}: it contains the project", returncode=2)
    if live_dir.exists() and any(live_dir.iterdir()):
        if not (live_dir / LIVE_MARKER_FILE).exists():
            pytest.exit(f"refusing to empty --live-dir={live_dir}: it has files that "
                        "an earlier live run did not write", returncode=2)
        shutil.rmtree(live_dir)
    live_dir.mkdir(parents=True, exist_ok=True)
    (live_dir / LIVE_MARKER_FILE).write_text("written by pytest --live; safe to delete\n")


def pytest_collection_modifyitems(config, items):
    live = config.getoption("--live")
    skip_live = pytest.mark.skip(reason="live-only test; run with --live")
    skip_write = pytest.mark.skip(
        reason="changes the service; run with --live --live-writes against a sandbox")
    for item in items:
        if not live and "live" in item.keywords:
            item.add_marker(skip_live)
        if live and "mutates" in item.keywords and not config.getoption("--live-writes"):
            item.add_marker(skip_write)


@pytest.fixture(scope="session")
def recording(record_mode):
    return record_mode != "none"


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    module = Path(request.node.path)
    committed = module.parent / "cassettes" / module.stem
    config = request.config
    if config.getoption("--live"):
        relative = committed.relative_to(config.rootpath)
        target = config._live_dir / relative
        config._recorded_dirs.add((committed, target))
        return str(target)
    if record_mode_of(config) != "none":
        config._recorded_dirs.add((committed, committed))
    return str(committed)


@pytest.fixture(scope="session")
def pseudonymizer(request, recording):
    key = os.environ.get(vcr_support.KEY_ENV, "")  # checked in pytest_configure
    originals = Path(os.environ.get(vcr_support.ORIGINALS_ENV)
                     or vcr_support.default_originals_path(request.config.rootpath))
    request.config._originals_path = originals
    # Replay never writes a cassette, so its key only has to be non-empty.
    return vcr_support.Pseudonymizer((key or "replay-only").encode(),
                                     originals if recording else None)


@pytest.fixture
def vcr_config(request, pseudonymizer):
    marker = request.node.get_closest_marker("synthetic_text")
    pseudonymizer.keep_text = {k.lower() for k in marker.args} if marker else set()
    yield pseudonymizer.vcr_config()
    pseudonymizer.keep_text = set()


@pytest.fixture(autouse=True)
def cassette_fully_played(vcr, recording):
    """In replay, every recorded request must be made again.

    Otherwise a test that skips a DELETE or its cleanup still passes.
    """
    yield
    if vcr is not None and not recording and not vcr.all_played:
        unplayed = [f"{r.method} {r.path}" for i, r in enumerate(vcr.requests)
                    if not vcr.play_counts[i]]
        pytest.fail(f"{len(unplayed)} recorded request(s) not made in replay: "
                    + ", ".join(unplayed), pytrace=False)


@pytest.fixture(scope="session")
def service_token(recording):
    """The real credential when talking to the service, a dummy in replay.

    Authorization headers are filtered from cassettes and not used for
    matching, so replay works without any secret on the machine.
    """
    if not recording:
        return "replay-token"
    token = LIVE_SERVICE_TOKEN
    if not token:
        pytest.skip(f"{SERVICE_TOKEN_ENV} not set; cannot reach the service")
    return token


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    pairs = getattr(config, "_recorded_dirs", set())
    if not pairs:
        return
    reporter = config.pluginmanager.get_plugin("terminalreporter")

    def write(message, **markup):
        if reporter:
            reporter.write_line(message, **markup)
        else:
            print(message)

    originals = vcr_support.Needles(
        vcr_support.read_list(getattr(config, "_originals_path", None)))
    allow = vcr_support.read_list(Path(__file__).resolve().parent / SCAN_ALLOW_FILE)

    leaks = []
    for _, written in sorted(pairs):
        for f in vcr_support.iter_files([written]):
            if f.name != LIVE_MARKER_FILE:
                leaks += [(f, where, kind, hit)
                          for where, kind, hit in vcr_support.scan_file(
                              f, originals, allow=allow)]
    if leaks:
        write("PRIVACY: recorded cassettes contain personal data or secrets "
              "(values redacted below). Extend the key lists in vcr_support.py "
              "or the scrubbing, delete the cassettes, and record again.", red=True)
        for f, where, kind, hit in leaks:
            write(f"  {f}:{where}: {kind} {hit}")
        session.exitstatus = 1

    if config.getoption("--live"):
        drift = []
        for committed, live in sorted(pairs):
            if committed.exists() and live.exists():
                drift += vcr_support.compare_directories(committed, live)
        hard = [f for f in drift if f[0] == "drift"]
        for sev, name, key, msg in drift:
            if msg != "not re-recorded in the live run":
                write(f"  {sev}: {name} {key}: {msg}", red=sev == "drift")
        if hard:
            write("DRIFT: the service no longer matches the committed cassettes. "
                  "Fix the code if needed, then re-record the affected tests with "
                  "--record-mode=rewrite -k <test> and review the diff.", red=True)
            session.exitstatus = 1
        else:
            write(f"live: no structural drift ({config._live_dir})", green=True)


# --- Project fixtures --------------------------------------------------

import atexit  # noqa: E402
import tempfile  # noqa: E402
import types  # noqa: E402

import typerconf  # noqa: E402

# Variables through which the developer's own setup reaches the code under
# test.  A test that needs one sets it with monkeypatch.setenv.
SERVICE_ENVIRONMENT = ("STAYAWHILE_API_KEY", "STAYAWHILE_BASE_URL",
                       "ONEDRIVE_BASE_URL")


def point_typerconf_at(directory):
    """Make typerconf read and write directory/config.json from now on.

    typerconf binds its file, ~/.config/<program>/config.json, as the
    default argument of read_config and write_config when it is imported.
    Replacing typerconf.dirs afterwards therefore changes nothing, and
    tests used to read and write ~/.config/pytest/config.json.  We replace
    the bound defaults instead, so the real typerconf code runs on a file
    of our choosing.  Returns the previous defaults and dirs.
    """
    directory = Path(directory)
    config_dir = directory / "typerconf-config"
    data_dir = directory / "typerconf-data"
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    conf_file = str(config_dir / "config.json")
    previous = [(method, method.__defaults__)
                for method in (typerconf.Config.read_config,
                               typerconf.Config.write_config)]
    previous_dirs = typerconf.dirs
    for method, defaults in previous:
        _, *other_defaults = defaults
        method.__defaults__ = (conf_file, *other_defaults)
    typerconf.dirs = types.SimpleNamespace(
        user_config_dir=str(config_dir),
        user_data_dir=str(data_dir),
        user_cache_dir=str(directory / "typerconf-cache"),
        user_log_dir=str(directory / "typerconf-log"))
    return previous, previous_dirs, Path(conf_file)


# Some code reads the configuration when it is imported, before any fixture
# can run: `kthutils config` (kthutils.cli) loads the file during collection
# and writes back to it.  So the whole session first gets a directory of its
# own, now, before the test modules are imported.
SESSION_TYPERCONF_DIR = Path(tempfile.mkdtemp(prefix="kthutils-tests-"))
atexit.register(shutil.rmtree, SESSION_TYPERCONF_DIR, ignore_errors=True)
point_typerconf_at(SESSION_TYPERCONF_DIR)


@pytest.fixture(autouse=True)
def isolated_typerconf(tmp_path):
    """Give each test an empty typerconf configuration of its own."""
    previous, previous_dirs, conf_file = point_typerconf_at(tmp_path)
    yield conf_file
    for method, defaults in previous:
        method.__defaults__ = defaults
    typerconf.dirs = previous_dirs


@pytest.fixture(autouse=True)
def isolated_service_environment(monkeypatch):
    """Remove the developer's service settings from the environment."""
    for name in SERVICE_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(scope="session")
def kth_session():
    """Return a function that builds a KTH session or skips the test.

    The sessions log in lazily with the credentials stored for ladok3, but
    their constructors already load those credentials.  Built at import,
    as the test modules used to, a missing credential aborted the
    collection of the whole module, offline tests included.
    """
    def build(factory):
        try:
            return factory()
        except (RuntimeError, KeyError, SystemExit) as err:
            pytest.skip(f"no KTH credentials ({type(err).__name__})")
    return build
