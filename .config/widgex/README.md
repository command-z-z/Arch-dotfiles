# Widgex desktop configuration

Native GTK3/Cairo profile. This directory remains linked to the Arch-dotfiles repository.

- Configuration: `~/.config/widgex/config.toml`
- Shared adapters: `scripts/`; module-specific helpers: `widgets/*/src/`
- Static resources: `assets/`, `pets/`, `widgets/wlogout/icons/`
- Runtime cache: `~/.cache/widgex/`
- Binaries: `~/.local/bin/widgex` and `~/.local/bin/widgexd`

```sh
widgex check
widgex daemon start
widgex open top-bar
widgex open clock
widgex open date
widgex open pet
widgex open weather
widgex open memo
widgex open sysstat
widgex open agent-monitor
widgex open --toggle dashboard
widgex open --toggle lyrics_overlay
widgex open --toggle wlogout
widgex daemon reload
widgex daemon stop
```

The notification bell opens the existing Swaync service. The unused `widgets/swaync`
module is a sample preview and is intentionally excluded from `config.toml`.
No login autostart was added; the commands above start the profile manually.

Migration backup (2026-09-13): `/home/eugene/.local/state/widgex/backups/20260913-101304`.
It contains both original profiles, the original shell configuration and cache snapshots.
To roll back, stop Widgex and restore the desired backup to the dotfiles symlink target.
