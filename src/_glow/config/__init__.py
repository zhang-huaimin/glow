import pytest

import os
import sys
import shutil
import logging
from pathlib import Path

from typing import Sequence
from pytest import ExitCode

_PluggyPlugin = object


def main(
    args: list[str] | os.PathLike[str] | None = None,
    plugins: Sequence[str | _PluggyPlugin] | None = None,
) -> int | ExitCode:
    """Perform an in-process test run.

    :param args:
        List of command line arguments. If `None` or not given, defaults to reading
        arguments directly from the process command line (:data:`sys.argv`).
    :param plugins: List of plugin objects to be auto-registered during initialization.

    :returns: An exit code.
    """
    this_file = Path(__file__).parent.absolute()
    workspace = Path(os.getcwd()).absolute()

    if not os.path.isdir(workspace):
        return ExitCode.USAGE_ERROR

    try:
        pyproject = this_file.joinpath("pyproject.toml")
        shutil.copy(this_file.joinpath("conftest.py"), workspace)

        _args = args if args else sys.argv
        sys.argv = _args

        pytest.main()
    except Exception as e:
        logging.error(e)
        return ExitCode.USAGE_ERROR
    finally:
        if workspace.joinpath("conftest.py").exists():
            os.unlink(workspace.joinpath("conftest.py"))


def console_main() -> int:
    """The CLI entry point of glow.

    This function is not meant for programmable use; use `main()` instead.
    """
    # https://docs.python.org/3/library/signal.html#note-on-sigpipe
    try:
        code = main()
        sys.stdout.flush()
        return code
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 1  # Python exits with error code 1 on EPIPE
