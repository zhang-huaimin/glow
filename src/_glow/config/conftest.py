import os
import shutil
import pytest
from pathlib import Path
from glow import ParallelClient
from glow import Dev
from glow import DevPool
from filelock import FileLock


WORKSPACE = Path(os.getcwd()).absolute()


def pytest_addoption(parser):
    parser.addoption(
        f"--conf",
        action="store",
        default="glow.toml",
        help="Dev Configs",
    )

    parser.addoption(
        f"--conf_dir",
        action="store",
        type=Path,
        default=WORKSPACE.joinpath("conf"),
        help="Dev Configs Dir",
    )

    parser.addoption(
        f"--log_dir",
        action="store",
        type=Path,
        default=WORKSPACE.joinpath("log"),
        help="Log Dir",
    )

    parser.addoption(
        f"--log_level",
        action="store",
        default="DEBUG",
        help="Logging level",
    )

    parser.addoption(
        f"--parallel",
        action="store_true",
        help="Enable Parallel testing",
    )

    parser.addoption(
        f"--id",
        action="store",
        help="Unique id of current glow process. Auto set by glow",
    )


# session
@pytest.fixture(scope="session")
def dev_pool(request):
    pyt_config = request.config.option.__dict__
    pyt_config["WORKSPACE"] = WORKSPACE
    id = pyt_config["id"]
    pool = None

    lock = WORKSPACE.joinpath(f".{id}.lock")
    own_lock = False
    db = WORKSPACE.joinpath(f".{id}.db")
    with FileLock(str(lock)):
        if os.path.getsize(lock) > 0:
            if pyt_config["parallel"]:
                pool = ParallelClient(db)
        else:
            own_lock = True
            lock.write_text("glow parallel lock")
            if pyt_config["log_dir"].exists():
                shutil.rmtree(pyt_config["log_dir"])

            pool = DevPool(pyt_config)
            if pyt_config["parallel"]:
                parallel_pool = ParallelClient(db)
                while not pool.empty():
                    parallel_pool.put(pool.get())
                pool = parallel_pool

    yield pool

    if own_lock and lock.exists():
        lock.unlink()


# class
@pytest.fixture(scope="class", autouse=True)
def dev(request, dev_pool):
    device: Dev = dev_pool.get()
    device.bind_cls(request.node)

    yield device

    device.unbind_cls()
    device = device.reinit() if device.pyt_config["parallel"] else device
    dev_pool.put(device)


# function
@pytest.fixture(scope="function", autouse=True)
def bind_func(request):
    device: Dev = request.cls.dev
    device.bind_func(request.node)

    yield

    device.unbind_func()
