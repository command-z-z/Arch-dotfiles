# Codex-linked desktop pet

The pet follows live local Codex sessions using the existing read-only adapter in
`../agent-monitor/src/codex_monitor.py`. It respects `CODEX_HOME` and selects a
running root session before the newest inactive root session, matching the monitor.

- Running: fast walking.
- Observed running turn completes: wave for 3 seconds, then ordinary roaming.
- Interrupted: wait in place until activity resumes or Codex exits.
- Offline or unknown: ordinary roaming.

An already completed session at startup does not trigger a completion wave.
The pet stays at the bottom edge and remains click-through.
No API keys, Codex hooks, or Codex configuration changes are required.

Run checks with `python3 -B test_codex_state.py`.
The Codex rollout format is internal and may need adaptation after a Codex update.
