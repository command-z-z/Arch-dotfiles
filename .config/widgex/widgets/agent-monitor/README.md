# Codex monitor

The active card reads live local Codex CLI sessions. It displays project/model,
turn status, recent activity category, elapsed time, tool count and last reported
context usage. It no longer reads Claude hook files or shows synthetic progress.

Source: `python3 -B ./src/codex_monitor.py --listen` (run from this module).
Run without `--listen` to inspect one JSON snapshot.

`module.toml` and `style.css` define the GTK UI. The card is 420x300 and remains
on the background layer. Normal application windows can cover it.

The adapter respects CODEX_HOME, uses /proc to find live Codex rollouts, and tails
incrementally. It does not install hooks or modify Codex configuration. Rollout
format is internal; this version was verified with Codex CLI 0.154.0.

Backup: ~/.local/state/widgex/backups/codex-monitor-20260913-103952
