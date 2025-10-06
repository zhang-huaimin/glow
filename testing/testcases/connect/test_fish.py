import pytest


class TestFish:
    @pytest.fixture(scope="class", autouse=True)
    def init_and_close(self):
        try:
            if self.con.protocol != "fish":
                pytest.skip()
                self.con.close()
            yield
        finally:
            pass

    def test_bind_fish(self):
        assert self.dev.con.shell.protocol == "fish"

    def test_connect_protocol(self):
        assert self.dev.con.protocol == "fish"

    def test_ask(self):
        self.con.ask("whoami; echo res:$status", "res:0")
        self.con.ask("whoami", self.dev.config.user)
