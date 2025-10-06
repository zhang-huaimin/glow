from __future__ import annotations

import logging
import re
import pytest
from time import sleep
from typing import Tuple
from abc import ABC, abstractmethod

from _glow.config.config import ConnectConfig, ShellConfig


class Connect(ABC):
    MIN_WAIT_TIME = 0.1
    buf = b""
    shell = None

    def __init__(self, config: ConnectConfig):
        self.config = config

    @property
    def protocol(self) -> str:
        return self.config.protocol

    @property
    def logger(self) -> logging.Logger:
        return self.dev.logger

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

    def __adapt_cmd(self, cmd: str) -> str:
        adapt_cmd = f"; echo GlowRes:{self.shell.exit_flag}"
        if re.search(r"[\r\n]\Z", cmd):
            return re.sub(r"([\r\n]+)\Z", rf"{adapt_cmd}\1", cmd)
        else:
            return cmd + adapt_cmd

    def send(self, cmd: str, adaptive: bool = False) -> str:
        """Send ``cmd`` to dev. If want to add **newline** at cmd's tail, should replace it with ``Connect.br()``

        :param cmd: cmd sended to dev.
        """
        cmd = self.__adapt_cmd(cmd) if adaptive else cmd
        self._send(cmd)
        return cmd

    def recv(self, time: float = 0.1) -> str:
        """Recv ``time`` secs data from dev.

        :param time: secs.
        """
        _data = b""
        sleep(time)
        self._recv()

        index = self.buf.rfind(b"\n")
        if index == -1:
            pass
        elif index == len(self.buf) - 1:
            _data, self.buf = self.buf, b""
        else:
            _data, self.buf = self.buf[: index + 1], self.buf[index + 1 :]

        data = _data.decode("utf-8")

        # FIXME：，如果cmd有换行符，则此方法会返回多行数据
        self.logger.debug(data)

        return data

    def br(self, cmd: str = "", adaptive: bool = False) -> str:
        """Send ``cmd`` with **newline** at tail to dev.

        :param cmd: cmd sended to dev.
        """
        return self.send(f"{cmd}\n", adaptive)

    def wait(
        self,
        expect: str = None,
        timeout: float = 5.0,
        err: str = None,
        soft: bool = False,
        unexpect: str = None,
    ) -> Tuple[bool, str]:
        """See ``Connect.ask()`` for details. The difference between them is that ``wait`` does not send cmd."""
        if not expect and not unexpect:
            raise ValueError("Expect or unexpect should not be None at the same time.")

        data = ""
        stat = False
        is_timeout = False

        if timeout < self.MIN_WAIT_TIME:
            raise ValueError(
                f"Argument timeoutt which is {timeout} should > {self.BASE_TIME} seconds."
            )

        max_times = int(timeout * (1 / self.MIN_WAIT_TIME))

        # TODO: 控制执行时间
        for i in range(max_times):
            is_pass = False
            is_fail = False

            data += self.recv(self.MIN_WAIT_TIME)

            if unexpect and re.search(unexpect, data):
                is_fail = True
            if expect and re.search(expect, data):
                is_pass = True

            stat = True if not is_fail and is_pass else False
            logging.error(f"is_pass: {is_pass}, is_fail: {is_fail}")

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
                self.logger.error(err)
                pytest.fail(err)

        return stat, data

    def ask(
        self,
        cmd: str,
        expect: str = None,
        timeout: float = 5.0,
        err: str = None,
        soft: bool = False,
        unexpect: str = None,
        adaptive: bool = False,
    ) -> Tuple[bool, str]:
        """
        let `dev` exec ``cmd``, expect get ``expect`` in ``timeout`` secs.

        1. *pass* test step if get ``expect``.
        2. *unexpect* test case if not get ``expect``, or get ``unexpect``.

        .. code-block:: python
            :caption: example
            :linenos:

            stat, data = self.dev.con.ask(
                cmd='ls; echo res:$?',
                expect='res:0',
                timeout=5,
                err="ls failed",
                soft=False,
                unexpect="res:[1-9]\\d*",
            )

            assert stat == True
            assert 'res:0' in data

        :param cmd: cmd sended to dev.
        :param expect: *pass* test step if get ``expect`` limit in ``timeout`` secs.
        :param timeout: timeout (unit: sec). *unexpect* test case if over.
        :param err: print it if *unexpect*.
        :param soft: *pass* test step whatever.
        :param unexpect: *unexpect* test case if get ``unexpect``.

        :returns: A tuple containing a bool of the cmd exec stat,
            and a str of cmd exec data.

        """
        if adaptive:
            if not expect:
                expect = "GlowRes:0"
            if not unexpect:
                unexpect = "GlowRes:[1-9]\\d*"

        may_adaptive_cmd = self.br(cmd, adaptive)

        if not err:
            err = f"Exec '{may_adaptive_cmd}' at {self.dev.type}:{self.dev.name} failed, no expect: '{expect}' match or unexpect: '{unexpect}' match."

        stat, data = self.wait(expect, timeout, err, soft, unexpect)

        return stat, data
