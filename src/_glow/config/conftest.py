import os
import pytest
from pathlib import Path
from glow import DevPool

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


# session
@pytest.fixture(scope="session")
def dev_pool(request):
    pool = None

    pyt_config = request.config.option.__dict__
    pyt_config["WORKSPACE"] = WORKSPACE
    pool = DevPool(pyt_config)

    yield pool
    # TODO: Add session close code


# class
@pytest.fixture(scope="class", autouse=True)
def dev(request, dev_pool):
    device = dev_pool.get()
    device.bind_cls(request.node)

    yield device

    device.unbind_cls()
    dev_pool.put(device)


# function
@pytest.fixture(scope="function", autouse=True)
def bind_func(request):
    device = request.cls.dev
    device.bind_func(request.node)

    yield

    device.unbind_func()
