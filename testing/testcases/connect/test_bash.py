import pytest


class TestBash:
    @pytest.fixture(scope="class", autouse=True)
    def init_and_close(self):
        try:
            if self.con.protocol != "bash":
                pytest.skip()
                self.con.close()
            yield
        finally:
            pass

    def test_bind_bash(self):
        assert self.dev.con.shell.protocol == "bash"

    def test_connect_protocol(self):
        assert self.dev.con.protocol == "bash"

    def test_ask(self):
        self.con.ask("whoami; echo res:$?", "res:0")
        self.con.ask("whoami", self.dev.config.user)
