import serial as ser

from _glow.config.config import SerialConfig
from _glow.connect.connect import Connect


class Serial(Connect):
    def __init__(self, config: SerialConfig):
        super().__init__(config)

        self.serial = ser.Serial(
            port=self.config.port, baudrate=self.config.baudrate, timeout=0
        )
        self.serial.flush()

    @property
    def port(self) -> str:
        return self.config.port

    @property
    def baudrate(self) -> int:
        return self.config.baudrate

    def check(self):
        return self.serial.is_open

    def _recv(self):
        self.buf += self.serial.read(65535)

    def _send(self, cmd: str):
        self.serial.write(cmd)

    def close(self):
        self.serial.close()
