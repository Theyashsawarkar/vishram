"""vishram (विश्राम, "rest"): the power menu for Vyom.

Lock, suspend, log out, reboot and power off, one letter each, as big
tiles: the safe ones (lock, suspend) apart from the final ones. Log out,
reboot and power off count down first (a ring that fills, in red; any key
cancels, Enter does it now) and warn about windows that look unsaved.
"""
import json
import os
import re
import shutil

from gi.repository import GLib, Gtk

from vyom import Plugin as Base
from vyom import Hint, ui, util

from . import vim

# KEYBINDS (generated from vishram/vim.py by scripts/keybinds.py; don't edit by hand)
# keybind: Vyom/power:normal | s | Suspend
# keybind: Vyom/power:normal | e | Log out (after a 5-second countdown)
# keybind: Vyom/power:normal | b | Reboot (after a 5-second countdown)
# keybind: Vyom/power:normal | p | Power off (after a 5-second countdown)
# keybind: Vyom/power:normal | Enter | Pick the focused action (Lock has the focus when the menu opens)
# keybind: Vyom/power countdown | Enter | Confirm the action now instead of waiting
# keybind: Vyom/power countdown | Esc | Cancel the countdown (any other key does too, Space included)
# END KEYBINDS


def default_logout():
    if os.environ.get("SWAYSOCK") and shutil.which("swaymsg"):
        return "swaymsg exit"
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
        return "hyprctl dispatch exit"
    if os.environ.get("NIRI_SOCKET") and shutil.which("niri"):
        return "niri msg action quit --skip-confirmation"
    return "loginctl terminate-session ${XDG_SESSION_ID:-self}"


ACTIONS = [  # key, letter, label, icon, color, countdown, "… in N s"
    ("lock", "Enter", "Lock", "\U000f033e", "blue", False, ""),
    ("suspend", "s", "Suspend", "\U000f04b2", "mauve", False, ""),
    ("logout", "e", "Log out", "\U000f0343", "yellow", True, "Logging out"),
    ("reboot", "b", "Reboot", "\U000f0709", "peach", True, "Rebooting"),
    ("poweroff", "p", "Power off", "\U000f0425", "red", True, "Powering off"),
]
STEP = 100   # ms between redraws of the countdown ring
# Keys that only modify another: pressing them alone doesn't cancel.
MODIFIERS = re.compile(r"^(Shift|Control|Alt|Super|Meta|Hyper|ISO_Level\d)_?[LR]?$|_Lock$")
# A window title that says it has unsaved changes: "*notes.txt - gedit",
# "● main.py - Code", "file [+] - NVIM", "Untitled (modified)", "… unsaved …".
UNSAVED = re.compile(r"^\s*[*●•]|[*●•]\s*$|\[\+\]|\(modified\)|\bunsaved\b", re.I)


def pretty_app(node):
    app = node.get("app_id") or (node.get("window_properties") or {}).get("class") or ""
    app = app.split(".")[-1] if "." in app else app       # dev.zed.Zed -> Zed
    app = re.sub(r"^libreoffice-?\w*$", "LibreOffice", app, flags=re.I)
    return app[:1].upper() + app[1:] if app else (node.get("name") or "a window")[:24]


def windows():
    """[(app, title)] of every open window on sway, or None when we can't
    tell (not sway): one `swaymsg -t get_tree`, cheap."""
    if not shutil.which("swaymsg"):
        return None
    code, out = util.run(["swaymsg", "-t", "get_tree"], timeout=2)
    if code:
        return None
    found = []

    def walk(node):
        if node.get("type") in ("con", "floating_con") and node.get("pid"):
            found.append((pretty_app(node), node.get("name") or ""))
        for c in node.get("nodes", []) + node.get("floating_nodes", []):
            walk(c)
    try:
        walk(json.loads(out))
    except (ValueError, AttributeError):
        return None
    return found


def unsaved(wins):
    """The apps whose window titles say they have unsaved work (once each)."""
    apps = []
    for app, title in wins or []:
        if UNSAVED.search(title) and app not in apps:
            apps.append(app)
    return apps


class Plugin(Base):
    name, title, icon, color = "vishram", "Power", "⏻", "red"
    layout = "card"
    width = 600
    modal = True                # vim keys (Vyom 0.7): always NORMAL; the card cursor moves between tiles
    start_mode = "normal"
    hints = [Hint("s e b p", "choose"), Hint("h / l", "move"), Hint("Enter", "pick (Lock first)")]

    def __init__(self, vyom, conf):
        super().__init__(vyom, conf)
        self.timer = None
        self.pending = None
        self.left_ms = self.total_ms = 0
        self.wins = None

    def command(self, key):
        defaults = {"lock": "loginctl lock-session", "suspend": "systemctl suspend", "logout": default_logout(),
                    "reboot": "systemctl reboot", "poweroff": "systemctl poweroff"}
        return self.conf.get(key, defaults[key])

    def build_card(self):
        self.cancel()
        # One row: the safe ones (lock, suspend), a gap, the final ones. Every
        # tile asks for the same width, so the spare space is shared equally.
        row = Gtk.Box(spacing=10)
        row.add_css_class("vishram-tiles")
        self.buttons, self.icons = {}, {}
        for key, letter, label, icon, color, counts, _ in ACTIONS:
            b = Gtk.Button(hexpand=True, width_request=112)
            b.add_css_class("vishram-btn")
            b.add_css_class(f"v-{color}")
            if counts:
                b.add_css_class("final")
            holder = Gtk.Box(halign=Gtk.Align.CENTER, height_request=54)
            holder.append(ui.label(icon, "vishram-icon", valign=Gtk.Align.CENTER))
            self.icons[key] = holder
            cap = ui.keycap(letter)
            cap.set_halign(Gtk.Align.CENTER)
            b.set_child(ui.vbox(holder, ui.label(label, "vishram-label"), cap, spacing=8))
            b.set_tooltip_text(f"{label} ({letter}" + (", it has the focus" if key == "lock" else "") + ")"
                               + (": counts down first" if counts else ""))
            b.connect("clicked", lambda _b, k=key: self.choose(k))
            self.buttons[key] = b
            if key == "logout":
                row.append(Gtk.Box(width_request=8))   # the gap between safe and final
            row.append(b)

        # The notice line is always there (a quiet note until a countdown), so
        # the panel never changes size under you.
        self.notice = Gtk.Box()
        self.show_idle()
        # The keys are in Vyom's footer (a modal card has one).
        card = ui.vbox(row, self.notice, spacing=18, cls="card")
        GLib.idle_add(self.first_focus)
        return card

    def first_focus(self):
        # Lock first. Vyom core draws where you are (vk-cursor; GTK's own
        # :focus doesn't show in a layer-shell panel).
        self.buttons["lock"].grab_focus()
        return False

    # ---------------------------------------------------------- countdown
    def choose(self, key):
        spec = next(a for a in ACTIONS if a[0] == key)
        if not spec[5]:
            self.run(key)
            return
        self.cancel()
        self.pending = key   # wants_all_keys(): from now on every key reaches key() first
        self.total_ms = self.left_ms = int(float(self.conf.get("countdown", 5)) * 1000)
        self.wins = None
        self.background(windows, then=self.got_windows)
        self.buttons[key].add_css_class("counting")
        self.buttons[key].grab_focus()
        self.show_notice()
        self.draw_ring()
        self.timer = GLib.timeout_add(STEP, self.tick)

    def got_windows(self, wins):
        if self.pending and not isinstance(wins, Exception):
            self.wins = wins
            self.show_notice()

    def secs(self):
        return max(1, -(-self.left_ms // 1000))   # rounded up: 5 4 3 2 1

    def show_notice(self):
        spec = next(a for a in ACTIONS if a[0] == self.pending)
        old = self.notice.get_first_child()
        if old is not None:
            self.notice.remove(old)
        title = ui.label(f"{spec[6]} in {self.secs()} s", "vishram-n-title", xalign=0)
        self.n_title = title
        text = ui.vbox(title, spacing=3, cls=None)
        text.set_hexpand(True)
        lost = unsaved(self.wins)
        if lost:
            n = len(lost)
            warn = ui.hbox(ui.label("\U000f0026", "glyph", "t-yellow"),
                           ui.label(f"{n} window{'s' if n != 1 else ''} may have unsaved work: {', '.join(lost)}",
                                    "vishram-n-text", xalign=0, wrap=True), spacing=6)
            text.append(warn)
        elif self.wins:
            n = len(self.wins)
            text.append(ui.label(f"{n} window{'s' if n != 1 else ''} open: "
                                 f"{'they' if n != 1 else 'it'} will be closed", "vishram-n-text", xalign=0))
        cancel = ui.button("Cancel", self.cancel, key="any key")
        now = ui.button("Now", self.now, "danger", key="Enter")
        box = ui.hbox(ui.label(spec[3], "glyph", "vishram-n-icon", valign=Gtk.Align.START), text,
                      ui.hbox(now, cancel, spacing=8), spacing=12, cls="vishram-notice")
        box.get_last_child().set_valign(Gtk.Align.CENTER)
        self.notice.append(box)
        box.set_hexpand(True)
        self.notice.set_visible(True)

    def show_idle(self):
        old = self.notice.get_first_child()
        if old is not None:
            self.notice.remove(old)
        n = int(float(self.conf.get("countdown", 5)))
        box = ui.hbox(ui.label("\U000f02fc", "glyph", "vishram-idle-icon"),
                      ui.label(f"Lock and suspend act at once. Log out, reboot and power off wait {n} s first: "
                               "any key cancels.", "vishram-idle-text", xalign=0, wrap=True, hexpand=True),
                      spacing=10, cls="vishram-idle")
        self.notice.append(box)
        box.set_hexpand(True)

    def draw_ring(self):
        holder = self.icons[self.pending]
        old = holder.get_first_child()
        if old is not None:
            holder.remove(old)
        done = 1 - self.left_ms / self.total_ms if self.total_ms else 1
        holder.append(ui.ring(max(0.02, done), "red", 52, 5, ui.label(str(self.secs()), "vishram-count")))

    def tick(self):
        if not self.pending:
            return False
        self.left_ms -= STEP
        if self.left_ms <= 0:
            key = self.pending
            self.timer = None
            self.cancel()
            self.run(key)
            return False
        self.draw_ring()
        self.n_title.set_label(f"{next(a[6] for a in ACTIONS if a[0] == self.pending)} in {self.secs()} s")
        return True

    def now(self):
        key = self.pending
        if key:
            self.cancel()
            self.run(key)

    def cancel(self):
        if self.timer:
            GLib.source_remove(self.timer)
        key, self.timer, self.pending = self.pending, None, None
        if key and hasattr(self, "icons"):
            spec = next(a for a in ACTIONS if a[0] == key)
            holder = self.icons[key]
            old = holder.get_first_child()
            if old is not None:
                holder.remove(old)
            holder.append(ui.label(spec[3], "vishram-icon", valign=Gtk.Align.CENTER))
            self.buttons[key].remove_css_class("counting")
        if hasattr(self, "notice"):
            self.show_idle()

    def run(self, key):
        self.close()
        # A beat for the panel to go away first (so a lock screen isn't covered).
        GLib.timeout_add(150, lambda: (util.spawn(self.command(key)), False)[1])

    def closed(self):
        self.cancel()

    def wants_all_keys(self):
        # During a countdown Vyom drops a half-typed key (Space, a count, an
        # open palette) and gives the next key to key(), so it cancels.
        return bool(self.pending)

    def key(self, name, row, mods):
        # A countdown: Enter does it now; any other key (Space and Esc too) cancels and does nothing else.
        if self.pending:
            if name in ("Return", "KP_Enter"):
                self.now()
                return True
            if MODIFIERS.search(name):
                return False
            self.cancel()
            return True
        return False

    # ------------------------------------------------------------ vim keys
    def keys(self, tab):
        return vim.keys(tab)

    def v_choose(self, _n, key):
        self.choose(key)
