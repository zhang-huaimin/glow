import tomllib
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings
from typing import Optional, Self, TypeAlias, Union, Literal

ShellType: TypeAlias = Literal["bash", "zsh", "fish", "sh"]


class SshConfig(BaseModel):
    protocol: Literal["ssh"]
    shell: ShellType = "bash"
    port: int = 22
    # set default by DevConfig
    hostname: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    # set default by DevConfig
    no_password: bool = False
    keyfile: Optional[Path] = None
    timeout: float = 10


class SerialConfig(BaseModel):
    protocol: Literal["serial"]
    shell: ShellType = "bash"
    port: str
    baudrate: int = 115200


class ShellConfig(BaseModel):
    protocol: ShellType
    shell: ShellType = ""  # same as protocol

    @model_validator(mode="after")
    def ensure_shell_matches(self) -> Self:
        if not self.shell:
            self.shell = self.protocol
        elif self.shell != self.protocol:
            raise ValueError("shell must be same as protocol")
        return self


ConnectConfig = Union[SshConfig, SerialConfig, ShellConfig]


class DevConfig(BaseModel):
    name: str
    type: str
    arch: str
    hostname: str
    user: str
    password: str
    workspace: Path
    connect: ConnectConfig = Field(..., discriminator="protocol")

    @model_validator(mode="after")
    def fill_ssh_defaults(self) -> Self:
        if isinstance(self.connect, SshConfig):
            ssh = self.connect
            if ssh.hostname is None:
                ssh.hostname = self.hostname
            if ssh.user is None:
                ssh.user = self.user
            if ssh.password is None:
                ssh.password = self.password
        return self


class Config(BaseSettings):
    dev: DevConfig


def load_config(conf: Path) -> Config:
    with open(conf, "rb") as f:
        data = tomllib.load(f)
    config = Config(**data)
    return config
