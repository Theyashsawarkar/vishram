# 3. Count down before log out, reboot and power off

**Status:** Accepted  
**Date:** 2026-10-19

## Context

One stray key in a power menu can lose unsaved work.

## Decision

Lock and suspend act at once; log out, reboot and power off count down five seconds (Esc cancels, Enter confirms) and show how many windows are open.

## Consequences

- Mistakes are recoverable.
- The countdown is configurable.
