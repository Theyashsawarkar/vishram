# Changelog

Newest first. Releases are tags (`vX.Y.Z`).

## v0.3.0 -- 2026-11-09

- Where you are on the menu is drawn by Vyom core (`vk-cursor`) instead of vishram's own focus watcher; the look (red while counting down) is the same.
- **No more accidental lock or reboot.** `Space` no longer presses the
  focused tile (Lock had the focus, so `Space` locked the screen); `l` no
  longer locks and `r` no longer reboots. Lock has the focus when the menu
  opens, so `Enter` locks; **reboot is `b`** (re**b**oot). `r` and `L` say
  where they went, for one release.
- **Vim keys** (Vyom 0.7): always NORMAL (there's nothing to type);
  `h` / `l`, `j` / `k`, `gg` / `G` move between the tiles and `Enter` picks
  one, `s` / `e` / `b` / `p` choose directly, `Space` is the leader
  (`Space ?` lists every key, `q` closes).
- While a countdown runs, `Enter` does it now and any other key, `Space`
  included, cancels it. **Fixed**: a countdown started by a click while a key was half-typed (`Space`, a count) let the next key finish that key instead of cancelling; the countdown now drops it (through Vyom's `wants_all_keys()`, so an open palette, help or confirm is dropped too).
- The tiles' keycaps are lowercase, like the keys (they said `L S E R P`,
  but Shift never worked); Vyom's footer shows the keys.
- Keys are data (`vishram/vim.py`); `scripts/keybinds.py` writes the
  `# keybind:` lines and the README table from it (`--check` in CI).
- Needs Vyom 0.7.0.

## v0.2.0 -- 2026-11-07

- **Big tiles, one letter each**, the safe ones (Lock, Suspend) apart from the final ones (Log out, Reboot, Power off); arrows and Enter work, with an accent frame on the tile you're on.
- **The countdown is a red ring that fills** in the chosen tile, with a red notice: "Powering off in 3 s", a Cancel button and a Now button.
- **Any key cancels the countdown** (Enter still does it now).
- **Warns about unsaved work** on sway: windows whose titles say so ("*notes.txt", "● main.py") are named; otherwise it says how many windows will be closed.
- The panel no longer changes size when a countdown starts or stops.
- The greeting header is gone: the tiles are the card.
- Needs Vyom 0.6.0.
- Every corner is rounded: the website's callouts.
- A logo and a shloka at the top of the README and the website: every Vayu tool has them now.

## v0.1.3 -- 2026-10-21

- Follows the theme: its colours are named (`@accent`, `@crust`...) instead
  of fixed hex codes, so a theme that redefines them (Vyom 0.2.9's `css`,
  e.g. [varna](https://github.com/Theyashsawarkar/varna)) recolours it too.

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
