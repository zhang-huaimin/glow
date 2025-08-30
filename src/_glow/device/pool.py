import importlib
from queue import Queue
from pathlib import Path
from types import ModuleType

from .conf import load_config
from .Glow import Glow
from .dev import Dev


def load_module_from_path(module_name: str, file_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        raise ModuleNotFoundError(f"Cannot load module {module_name} from {file_path}")


class DevPool:
    def __init__(self, pyt_config: dict) -> None:
        self.pool = Queue()
        self.pyt_config = pyt_config
        self.conf_dir = Path(pyt_config["conf_dir"])

        dev_confs = pyt_config["conf"]

        registeds = set()
        for _dev_conf in dev_confs.split(","):
            dev_conf = self.conf_dir.joinpath(f"{_dev_conf.strip()}.toml")
            if dev_conf in registeds:
                continue
            registeds.add(dev_conf)

            dev_config = load_config(dev_conf).dev

            dev_cls = self.__get_dev_cls(dev_config.type)
            self.put(dev_cls(dev_conf, pyt_config))

    def put(self, dev: Dev):
        self.pool.put(dev)

    def get(self) -> Dev:
        return self.pool.get()

    def empty(self) -> bool:
        return self.pool.empty()

    def __get_dev_cls(self, dev_type: str) -> Dev:
        dev_cls = None
        dev_type_file = self.conf_dir.joinpath(f"{dev_type}.py")

        if dev_type_file.exists():
            dev_module = load_module_from_path(dev_type, dev_type_file)
            dev_cls = getattr(dev_module, dev_type)
        else:
            dev_cls = Glow

        return dev_cls
