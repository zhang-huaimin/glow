import paramiko

from _glow.connect.connect import Connect
from _glow.config.config import SshConfig


class Ssh(Connect):
    def __init__(self, config: SshConfig):
        super().__init__(config)

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.config.no_password or self.config.keyfile:
            self.ssh.connect(
                hostname=self.config.hostname,
                port=self.config.port,
                username=self.config.user,
                key_filename=str(self.config.keyfile) if self.config.keyfile else None,
                timeout=self.config.timeout,
            )
        else:
            self.ssh.connect(
                hostname=self.config.hostname,
                port=self.config.port,
                username=self.config.user,
                password=self.config.password,
                timeout=self.config.timeout,
            )

        self.ssh.get_transport().set_keepalive(60)
        self.channel = self.ssh.invoke_shell()
        self.channel.setblocking(0)
        self.channel.settimeout = 1

    @property
    def hostname(self) -> str:
        return self.config.hostname

    @property
    def port(self) -> int:
        return self.config.port

    @property
    def user(self) -> str:
        return self.config.user

    @property
    def password(self) -> str:
        return self.config.password

    def check(self) -> bool:
        return not self.channel.closed and self.channel.active

    def _recv(self):
        if self.channel.recv_ready():
            self.buf += self.channel.recv(65535)

    def _send(self, cmd: str):
        self.channel.send(cmd)

    def close(self):
        self.channel.close()
        self.ssh.close()
