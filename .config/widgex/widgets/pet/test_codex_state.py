import importlib.util
from pathlib import Path
import sys
import unittest

MODULE = Path(__file__).with_name("codex_state.py")

class CodexPetTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.exists(), "Pet has no Codex state adapter")
        spec = importlib.util.spec_from_file_location("pet_codex_state", MODULE)
        self.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.module
        spec.loader.exec_module(self.module)

    def test_running_done_wave_once_and_new_turn_cancels_wave(self):
        r = self.module.Reaction()
        r.accept(("done", "session", "old"), 0)
        self.assertEqual(r.mode(0), "idle")
        r.accept(("running", "session", "new"), 1)
        self.assertEqual(r.mode(1), "running")
        r.accept(("done", "session", "new"), 2)
        self.assertEqual(r.mode(2), "wave")
        r.accept(("done", "session", "new"), 3)
        self.assertEqual(r.mode(5.1), "idle")
        r.accept(("running", "session", "next"), 5.2)
        self.assertEqual(r.mode(5.2), "running")

    def test_interrupted_waits_and_offline_resumes_idle(self):
        r = self.module.Reaction()
        r.accept(("running", "s", "turn"), 0)
        r.accept(("interrupted", "s", "turn"), 1)
        self.assertEqual(r.mode(1), "waiting")
        r.accept(("offline", "", ""), 2)
        self.assertEqual(r.mode(2), "idle")

    def test_other_session_completion_does_not_trigger_wave(self):
        r = self.module.Reaction()
        r.accept(("running", "s1", "t1"), 0)
        r.accept(("done", "s2", "t2"), 1)
        self.assertEqual(r.mode(1), "idle")

    def test_collector_matches_monitor_selection_and_dead_process_cleanup(self):
        m = self.module.monitor
        tracker = self.module.Tracker()
        active = m.Session(id="s1", state="running", turn_id="t1", started=1)
        done = m.Session(id="s2", state="done", turn_id="t2", started=2)
        self.assertEqual(tracker.select([active, done], 2), ("running", "s1", "t1"))
        self.assertEqual(tracker.select([], 0), ("offline", "", ""))
        self.assertEqual(tracker.select([], 1), ("unknown", "", ""))

if __name__ == "__main__":
    unittest.main()
