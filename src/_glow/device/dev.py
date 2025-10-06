import logging
from pathlib import Path

from _glow.connect import create_connect
from _glow.connect.connect import Connect
from ..config.config import DevConfig, load_config
from _pytest.python import Function, Class


class Dev:
    def __init__(self, conf: Path, pyt_config: dict):
        self.config: DevConfig = load_config(conf).dev
        self.conf = conf
        self.pyt_config = pyt_config

        self.logfile: Path = None
        self.logger: logging.Logger = None
        self.log_level: int = logging.getLevelNamesMapping()[
            self.pyt_config["log_level"]
        ]

        self.con: Connect = None
        self.cls_node: Class = None
        self.cls = None
        self.module_node: Class = None
        self.module = None
        self.func_node: Class = None
        self.func = None

    @property
    def name(self):
        return self.config.name

    @property
    def type(self) -> str:
        return self.config.type

    def prepare_test(self):
        pass

    def bind_cls(self, cls_node: Class):
        self.cls_node = cls_node
        self.cls = cls_node.cls
        self.cls.dev = self

        self.module = self.cls_node.parent
        self.logfile: Path = self.pyt_config["log_dir"].joinpath(
            self.module.nodeid.rstrip(".py") + ".log"
        )

        self.bind_connect()
        self.cls.con = property(lambda self: self.dev.con)

        self.module_node = self.cls_node.parent

        logger = logging.getLogger(
            f"{self.cls_node.nodeid}-{self.name}::{self.con.protocol}"
        )
        self.bind_logger(logger)
        self.cls.logger = self.logger
        self.cls.logger.info(f"***Test Class Start***: {self.cls.__name__}")

        self.prepare_test()

    def unbind_cls(self):
        self.cls.logger.info(f"***Test Class End***: {self.cls.__name__}")
        self.logger = None
        self.cls_node = None
        self.cls = None
        self.module_node = None

    def bind_func(self, func_node: Function):
        self.func_node = func_node
        self.func = func_node.function
        logger = logging.getLogger(
            f"{self.func_node.nodeid}-{self.name}::{self.con.protocol}"
        )
        self.bind_logger(logger)
        self.func.logger = self.logger
        self.func.logger.info(f"***Test Func Start***: {self.func_node.name}")

    def unbind_func(self):
        self.func.logger.info(f"***Test Func End***: {self.func_node.name}")
        self.func.logger = None
        self.func_node = None
        self.func = None

    def bind_connect(self):
        if self.con:
            if not self.con.check():
                try:
                    self.con.close()
                except Exception as e:
                    self.logger.warning(
                        f"Close connect {self.con.protocol} failed, cause of {e}."
                    )
                    del con
        con = create_connect(self.config.connect)
        con.dev = self
        self.con = con

    def bind_logger(self, logger: logging.Logger):
        self.logfile.parent.mkdir(exist_ok=True, parents=True)
        logger.setLevel(self.log_level)

        fd = logging.FileHandler(self.logfile)
        fd.setLevel(self.log_level)
        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s]\n%(message)s"
        )
        fd.setFormatter(formatter)
        logger.addHandler(fd)

        self.logger = logger
