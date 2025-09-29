from abc import ABC, abstractmethod
import re
from typing import Tuple

import pytest
from _glow.config.config import ConnectConfig
from time import sleep


class Connect(ABC):
    MIN_WAIT_TIME = 0.1
    buf = b""

    def __init__(self, config: ConnectConfig):
        self.config = config

    @property
    def protocol(self) -> str:
        return self.config.protocol

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def _send(self, cmd: str):
        """send str to dev.

        :param cmd: cmd sended to dev.
        """
        pass

    @abstractmethod
    def _recv(self) -> bytes:
        """recv bytes from dev. And please add it into self.buf!"""
        pass

    def send(self, cmd: str):
        """Send ``cmd`` to dev. If want to add **newline** at cmd's tail, should replace it with ``Connect.br()``

        :param cmd: cmd sended to dev.
        """
        self._send(cmd)

    def recv(self, t: float = 0.1) -> str:
        """Recv ``t`` secs data from dev.

        :param t: secs.
        """
        _data = b""
        sleep(t)
        self._recv()

        index = self.buf.rfind(b"\n")
        if index == -1:
            pass
        elif index == len(self.buf) - 1:
            _data, self.buf = self.buf, b""
        else:
            _data, self.buf = self.buf[: index + 1], self.buf[index + 1 :]

        data = _data.decode("utf-8")

        return data

    def br(self, cmd: str = ""):
        """Send ``cmd`` with **newline** at tail to dev.

        :param cmd: cmd sended to dev.
        """
        self.send(f"{cmd}\n")

    def wait(
        self,
        hope: str,
        t: float = 5.0,
        err: str = "",
        soft: bool = False,
        fail: str = "",
    ) -> Tuple[bool, str]:
        """See ``Connect.ask()`` for details. The difference between them is that ``wait`` does not send cmd."""

        timeout = t
        data = ""
        stat = False
        is_timeout = False

        if timeout < self.MIN_WAIT_TIME:
            raise ValueError(
                f"Argument t which is {t} should > {self.BASE_TIME} seconds."
            )

        max_times = int(timeout * (1 / self.MIN_WAIT_TIME))

        # TODO: 控制执行时间
        for i in range(max_times):
            is_pass = False
            is_fail = False

            data += self.recv(self.MIN_WAIT_TIME)
            if re.search(hope, data):
                is_pass = True
            if fail != "" and re.search(fail, data):
                is_fail = True

            stat = True if not is_fail and is_pass else False

            if is_pass or is_fail:
                break

            if i == max_times - 1:
                stat = False
                is_timeout = True

        if err and is_timeout:
            err = f"**Timeout {timeout} seconds** {err}"

        if not stat and err:
            # TODO: Log
            if not soft:
                print(err)
                print(data)
                pytest.fail(err)

        return stat, data

    def ask(
        self,
        cmd: str,
        hope: str = "",
        t: float = 5.0,
        err: str = "",
        soft: bool = False,
        fail: str = "",
    ) -> Tuple[bool, str]:
        """
        let `dev` exec ``cmd``, expect get ``hope`` in ``t`` secs.

        1. *pass* test step if get ``hope``.
        2. *fail* test case if not get ``hope``, or get ``fail``.

        .. code-block:: python
            :caption: example
            :linenos:

            stat, data = self.dev.con.ask(
                cmd='ls; echo res:$?',
                hope='res:0',
                t=5,
                err="ls failed",
                soft=False,
                fail="res:[1-9]\\d*",
            )

            assert stat == True
            assert 'res:0' in data

        :param cmd: cmd sended to dev.
        :param hope: *pass* test step if get ``hope`` limit in ``t`` secs.
        :param t: timeout (unit: sec). *fail* test case if over.
        :param err: print it if *fail*.
        :param soft: *pass* test step whatever.
        :param fail: *fail* test case if get ``fail``.

        :returns: A tuple containing a bool of the cmd exec stat,
            and a str of cmd exec data.

        """

        # TODO: 根据目标操作系统类型设置hope默认值
        if not hope:
            hope = "res:0"

        if hope == "res:0" and not fail:
            fail = "res:[1-9]\\d*"
        pass

        if not err:
            err = f"Exec '{cmd}' at {self.dev.type}:{self.dev.name} failed, no hope: '{hope}' match or fail: '{fail}' match."

        self.br(cmd)

        stat, data = self.wait(hope, t, err, soft, fail)

        return stat, data
