class TestConnect:
    def test_ask(self):
        self.con.ask("ls", adaptive=True)
        self.con.ask("whoami", adaptive=True)
