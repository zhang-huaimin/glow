from _glow.connect.ssh import Ssh
from _glow.connect.shell import Bash, Zsh, Fish, Sh
from _glow.connect.serial import Serial
from _glow.connect.connect import Connect
from _glow.config.config import (
    ConnectConfig,
    ShellConfig,
    ShellType,
)


_CONFIG_TO_CONNECT = {
    "ssh": Ssh,
    "serial": Serial,
    "bash": Bash,
    "zsh": Zsh,
    "fish": Fish,
    "sh": Sh,
}


def create_connect(config: ConnectConfig) -> Connect:
    con: Connect = _CONFIG_TO_CONNECT[config.protocol](config)
    con.shell = _CONFIG_TO_CONNECT[con.config.shell](config, complete=False)
    return con


def set_connect_shell(con: Connect, shell: str = ShellType):
    config: ConnectConfig = ShellConfig(protocol=shell, shell=shell)
    con.shell = _CONFIG_TO_CONNECT[shell](config, complete=False)


def reset_connect_shell(con: Connect):
    con.shell = _CONFIG_TO_CONNECT[con.config.shell](con.config, complete=False)
