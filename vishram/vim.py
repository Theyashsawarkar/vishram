"""vishram's vim keys, as data. A card: always NORMAL (nothing to type), and
Vyom's card cursor moves between the tiles (h / l, j / k, gg / G; Enter
picks the focused one). Lock has the focus when the menu opens, so Enter
locks; the other four have a letter each. No single letter locks or
reboots by accident any more: l moves right, r is free (reboot is b).
While a countdown runs, Enter does it now and any other key, Space too,
cancels it (vishram's key() sees the keys first).

An action "verb:arg" runs Plugin.v_<verb>(count, arg) in vishram/__init__.py,
or Vyom's own (moved, nop...).
"""
from vyom.keys import Bind

B = Bind
CARD = True


def moved(seq, to):
    """An old key that moved in v0.4 (for one release): says where to."""
    return B(seq, f"moved:{to}", "", hidden=True)


NORMAL = [
    B("s", "choose:suspend", "Suspend"),
    B("e", "choose:logout", "Log out (after a 5-second countdown)"),
    B("b", "choose:reboot", "Reboot (after a 5-second countdown)"),
    B("p", "choose:poweroff", "Power off (after a 5-second countdown)"),
    B("<CR>", "press", "Pick the focused action (Lock has the focus when the menu opens)"),
    moved("r", "b (reboot)"),
    moved("L", "Enter (Lock has the focus)"),
]

COUNTDOWN = [
    B("<CR>", "nop", "Confirm the action now instead of waiting"),
    B("<Esc>", "nop", "Cancel the countdown (any other key does too, Space included)"),
]

SECTIONS = [
    ("power", "normal", "Keys (it's always in NORMAL mode: there's nothing to type)", NORMAL),
    ("power countdown", "any", "While a countdown runs", COUNTDOWN),
]


def keys(_tab):
    return NORMAL
