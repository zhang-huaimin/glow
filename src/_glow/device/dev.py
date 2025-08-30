from pathlib import Path
from .conf import DevConfig, load_config
from _pytest.python import Function, Class


class Dev:
    def __init__(self, conf: Path, pyt_config: dict):
        self.config = load_config(conf).dev
        self.conf = conf
        self.pyt_config = pyt_config

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

        # TODO: self.init_connects()
        # support: use self.con in test class
        # TODO: log
        module = self.cls_node.parent
        self.prepare_test()

    def unbind_cls(self):
        pass

    def bind_func(self, func_node: Function):
        self.func_node = func_node
        self.func = func_node.function

    def unbind_func(self):
        pass
