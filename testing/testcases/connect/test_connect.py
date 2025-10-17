import pytest
from _pytest.outcomes import Failed


class TestConnect:
    def test_send_then_recv(self):
        self.con.send("whoami\n", adaptive=True)
        data = self.con.recv(2)
        assert self.dev.config.user in data

    def test_bind_connect(self):
        assert self.dev.con == self.con

    def test_ask_expect(self):
        self.con.ask("whoami", adaptive=True)
        self.con.ask(cmd="whoami", expect=self.dev.config.user, adaptive=True)

    def test_ask_timeout(self):
        self.con.ask("whoami", timeout=5, adaptive=True)
        try:
            self.con.ask(cmd="whoami", expect="anyway", timeout=2)
            raise AssertionError("Argument `timeout` is not working.")
        except Failed as e:
            assert "Timeout" in str(e)
        except Exception as e:
            raise AssertionError("Test ask argument `timeout` got other error: {e}.")

    def test_ask_unexpect(self):
        with pytest.raises(Failed):
            self.con.ask("whoami", unexpect="GlowRes:0", adaptive=True)
            raise AssertionError("Argument `unexpect` is not working.")

    def test_ask_err(self):
        with pytest.raises(Failed):
            self.con.ask(
                "whoami", err="Should Fail", unexpect="GlowRes:0", adaptive=True
            )

    def test_ask_soft(self):
        self.con.ask("whoami", soft=True, unexpect="GlowRes:0", adaptive=True)

    def test_ask_adaptive(self):
        self.con.ask("whoami", adaptive=True)
