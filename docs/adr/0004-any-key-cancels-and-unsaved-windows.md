# 4. Any key cancels the countdown, and unsaved windows are named

**Status:** Accepted (refines 3)  
**Date:** 2026-11-07

## Context

Decision 3 counts down five seconds before log out, reboot and power off, with Esc to cancel. Someone who chose a final action by mistake reaches for whatever key is under their hand, not necessarily Esc; and the window count alone doesn't say which window holds work that would be lost.

## Decision

While counting down, any key except Enter cancels (Enter still does it now; Shift, Ctrl and the other modifiers alone do nothing). The countdown is a red ring that fills in the chosen tile, with a red notice ("Powering off in 3 s", "Cancel · any key").

On sway, one `swaymsg -t get_tree` when the countdown starts lists the open windows; titles that mark unsaved changes (a leading or trailing `*` or `●`, `[+]`, "(modified)", "unsaved") are named in the notice. Otherwise it says how many windows will be closed. Nothing else is probed: no per-app checks.

## Consequences

- A stray press stops the countdown instead of passing it by.
- The unsaved warning is a hint, not a guarantee: apps that don't mark their titles (LibreOffice, for one) aren't caught, and the README says so.
- Other compositors get no window list (and no warning) until someone adds their query.
