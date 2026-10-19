# Changelog

Newest first. Releases are tags (`vX.Y.Z`).

## v0.1.0 -- 2026-10-19

- First release, as its own repository: the power menu. Replaces nwg-bar in Vayu.
- Lock, suspend, log out, reboot and power off, **one letter each** (`L S E R P`).
- Log out, reboot and power off **count down 5 seconds first** (Esc cancels, Enter does it now), showing how many windows are still open.
- Log out works on sway, Hyprland and niri out of the box (else `loginctl terminate-session`).
