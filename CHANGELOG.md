# Changelog

Newest first. Releases are tags (`vX.Y.Z`).

## v0.1.2 -- 2026-10-21

- A website (GitHub Pages, https://theyashsawarkar.github.io/vishram/): the README as a home page, the
  changelog, and architecture decision records (`docs/adr/`), built from these files by
  `scripts/build-site.py`; CI checks the site is up to date.

## v0.1.1 -- 2026-10-21

- Documentation for open source: a logo and banner, a full README (features,
  install, usage, configuration, troubleshooting, the whole Vyom family),
  CONTRIBUTING, SECURITY and CODE_OF_CONDUCT, issue and pull request
  templates, and CI (compiles, checks plugin.toml and that every key is
  documented).

## v0.1.0 -- 2026-10-19

- First release, as its own repository: the power menu. Replaces nwg-bar in Vayu.
- Lock, suspend, log out, reboot and power off, **one letter each** (`L S E R P`).
- Log out, reboot and power off **count down 5 seconds first** (Esc cancels, Enter does it now), showing how many windows are still open.
- Log out works on sway, Hyprland and niri out of the box (else `loginctl terminate-session`).
