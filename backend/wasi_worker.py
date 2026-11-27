"""Trusted subprocess. Only packaged CPython/WASI evaluates the staged sources."""
import json
from importlib import metadata
from pathlib import Path
import sys
import threading
from zipfile import ZIP_STORED, ZipFile

from wasi_python import Grant, run


def package_dependencies(directory):
    # Only public Python sources/metadata from the runner dependencies enter the guest.
    with ZipFile(directory / "deps.zip", "w", compression=ZIP_STORED) as archive:
        for package in ("pytest", "pluggy", "iniconfig", "coverage", "packaging", "pygments"):
            distribution = metadata.distribution(package)
            for item in distribution.files or ():
                if ".." in item.parts or item.is_absolute():
                    continue
                if item.suffix == ".py" or (item.name == "METADATA" and item.parent.name.endswith(".dist-info")):
                    archive.write(distribution.locate_file(item), item.as_posix())


def main():
    job, cache = Path.cwd(), Path(sys.argv[2]).resolve()
    packages = job / "packages"
    packages.mkdir()
    package_dependencies(packages)
    guest = Path(__file__).with_name("guest_pytest.py").read_text(encoding="utf-8")
    cancel = threading.Event()
    # The worker never executes an uploaded command. Its only guest program is this test harness.
    with (job / "stdout.log").open("wb") as stdout, (job / "stderr.log").open("wb") as stderr:
        def capture(chunk):
            stream = stdout if chunk.stream == "stdout" else stderr
            stream.write(chunk.data)
            stream.flush()
            if chunk.cut:
                cancel.set()

        argv = ["-c", guest]
        if sys.argv[3:] == ["detailed"]:
            argv.append("detailed")
        result = run(
            argv,
            grants=[Grant(job / "work", "/work"), Grant(packages, "/deps")],
            import_path=["/deps/deps.zip"], root=False, env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
            memory_bytes=256 << 20, deadline_s=int(sys.argv[1]), output_bytes=256 << 10,
            max_open_files=128, cache_dir=cache, on_output=capture, cancel=cancel,
        )
    print(json.dumps({"exit_code": result.exit_code, "trapped": result.trapped, "cut": result.truncated}))


if __name__ == "__main__":
    main()
