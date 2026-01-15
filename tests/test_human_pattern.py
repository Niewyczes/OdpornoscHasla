from human_pattern_test import run_human_pattern_test

class MockApp:
    def __init__(self):
        self.stop_test = False
        self.attempts = 0
        self.stop_event = type("", (), {"is_set": lambda s: False})()

    def load_hybrid_passwords(self):
        return {
            "names": ["adam"],
            "adjectives": ["cool"],
            "special": ["!"]
        }

    def finish_human_pattern_test(self, password, found, matched, elapsed):
        self.found = found

def test_human_pattern_simple():
    app = MockApp()
    run_human_pattern_test(app, "adam123")
    assert app.found is True
