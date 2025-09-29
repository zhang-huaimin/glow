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

        self.con: Connect = None
        self.cls_node: Class = None
        self.cls = None
        self.module_node: Class = None
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

        self.bind_connect()
        self.cls.con = property(lambda self: self.dev.con)

        self.module_node = self.cls_node.parent
        self.prepare_test()

    def unbind_cls(self):
        self.cls_node = None
        self.cls = None
        self.module_node = None

    def bind_func(self, func_node: Function):
        self.func_node = func_node
        self.func = func_node.function

    def unbind_func(self):
        self.func_node = None
        self.func = None

    def bind_connect(self):
        if self.con:
            if not self.con.check():
                try:
                    self.con.close()
                except Exception:
                    # TODO: log
                    del con
        con = create_connect(self.config.connect)
        con.dev = self
        self.con = con
