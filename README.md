# vishram

**vishram** (विश्राम, "rest") — The power menu. A tool for [Vyom](https://github.com/Theyashsawarkar/vyom), the keyboard-driven panels of [Vayu](https://github.com/Theyashsawarkar/vayu); in Vayu it replaces nwg-bar.

> Power menu: lock, suspend, log out, reboot, power off; one letter each, a 5-second countdown with cancel for the final ones.

## Features

- Lock, suspend, log out, reboot and power off, **one letter each** (`L S E R P`).
- Log out, reboot and power off **count down 5 seconds first** (Esc cancels, Enter does it now), showing how many windows are still open.
- Log out works on sway, Hyprland and niri out of the box (else `loginctl terminate-session`).

## Keys

| Key | Action |
|---|---|
| `L` | Lock the screen |
| `S` | Suspend |
| `E` | Log out (after a 5-second countdown) |
| `R` | Reboot (after a 5-second countdown) |
| `P` | Power off (after a 5-second countdown) |
| `Enter (counting down)` | Do it now instead of waiting |
| `Esc (counting down)` | Cancel the countdown |
| `Esc` | close |

Every Vyom panel also has: `Up`/`Down` (or `Ctrl+K`/`Ctrl+J`) to move, `Page Up`/`Page Down`, `Tab` to switch to the next tool.

## Requirements

- [Vyom](https://github.com/Theyashsawarkar/vyom) 0.2 or newer (Python 3.11+, GTK 4, gtk4-layer-shell, a layer-shell compositor)

## Install

```sh
git clone https://github.com/Theyashsawarkar/vishram ~/.local/share/vyom/plugins/vishram
vyom reload        # or log out and in
vyom vishram         # open it (again: close it)
```

Bind it to a key, e.g. in sway:

```
bindsym $mod+<key> exec vyom vishram
```

Update: `git -C ~/.local/share/vyom/plugins/vishram pull && vyom reload`. `vyom list` shows every installed tool and why one would be skipped.

## Configuration

In `~/.config/vyom/config.toml` (all optional):

```toml
[plugin.vishram]
# lock / suspend / logout / reboot / poweroff: the command for each (default: loginctl lock-session, systemctl …)
# countdown: seconds before log out / reboot / power off (default: 5)
```

## License

MIT.
