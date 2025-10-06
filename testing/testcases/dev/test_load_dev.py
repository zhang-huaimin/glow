class TestLoadDevs:
    def test_load_dev(self):
        assert self.dev.name == self.dev.config.name

    def test_bind_connect(self):
        assert self.dev.con.protocol == self.dev.config.connect.protocol
        assert self.dev.con == self.con
        self.con.ask("whoami", adaptive=True)
