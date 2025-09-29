import tomllib
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings
from typing import Optional, Self, Union, Literal


class SshConfig(BaseModel):
    protocol: Literal["ssh"]
    port: int = 22
    # set default by DevConfig
    hostname: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    # set default by DevConfig
    no_password: bool = False
    keyfile: Optional[Path] = None
    timeout: float = 10
    no_password: bool = False


class SerialConfig(BaseModel):
    protocol: Literal["serial"]
    port: str
    baudrate: int = 115200


class BashConfig(BaseModel):
    protocol: Literal["bash"]


class ZshConfig(BaseModel):
    protocol: Literal["zsh"]


class FishConfig(BaseModel):
    protocol: Literal["fish"]


class ShConfig(BaseModel):
    protocol: Literal["sh"]


ConnectConfig = Union[
    SshConfig, SerialConfig, BashConfig, ZshConfig, FishConfig, ShConfig
]


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
