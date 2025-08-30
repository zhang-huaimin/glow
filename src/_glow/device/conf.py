# models.py
import tomllib
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ConnectConfig(BaseModel):
    type: str


class DevConfig(BaseModel):
    name: str
    type: str
    arch: str
    ip: str
    user: str
    passwd: str
    workspace: Path
    connect: ConnectConfig


class Config(BaseSettings):
    dev: DevConfig


def load_config(config: Path) -> Config:
    with open(config, "rb") as f:
        data = tomllib.load(f)
    return Config(**data)
