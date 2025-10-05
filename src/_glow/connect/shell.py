import os
import pty
import subprocess
from typing import Literal
from _glow.connect.connect import Connect
from _glow.config.config import ShellConfig

ENCODING = "utf-8"


class Shell(Connect):
    exit_flag = Literal["$?", "$status"]

    def __init__(
        self,
        config: ShellConfig,
        complete: bool = True,
    ):
        super().__init__(config)

        if complete:
            self.master, self.slave = pty.openpty()
            os.set_blocking(self.master, False)
            os.set_blocking(self.slave, False)
            self.shell = subprocess.Popen(
                ["bash", "-c", self.config.protocol],
                stdin=self.slave,
                stdout=self.slave,
                stderr=self.slave,
                encoding=ENCODING,
                close_fds=True,
                preexec_fn=os.setsid,
            )

    def check(self) -> bool:
        return self.shell.poll() is None

    def _recv(self):
        try:
            self.buf += os.read(self.master, 65535)
        except BlockingIOError:
            pass

    def _send(self, cmd: str):
        os.write(self.master, (cmd).encode(ENCODING))

    def close(self):
        try:
            os.close(self.master)
            os.close(self.slave)
            self.shell.terminate()
        except Exception:
            self.shell.kill()


class Sh(Shell):
    exit_flag = "$?"

    def __init__(self, config):
        super().__init__(config)


class Bash(Shell):
    exit_flag = "$?"


class Zsh(Shell):
    exit_flag = "$?"


class Fish(Shell):
    exit_flag = "$status"
