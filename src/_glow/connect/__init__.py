from _glow.connect.ssh import Ssh
from _glow.connect.shell import Bash, Zsh, Fish, Sh
from _glow.connect.serial import Serial
from _glow.connect.connect import Connect
from _glow.config.config import (
    ConnectConfig,
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
    return _CONFIG_TO_CONNECT[config.protocol](config)
