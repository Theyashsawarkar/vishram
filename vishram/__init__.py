"""vishram (विश्राम, "rest"): the power menu for Vyom.

Lock, suspend, log out, reboot and power off, one letter each. Log out,
reboot and power off wait 5 seconds with a countdown first (Esc cancels,
Enter does it now), and the header says how many windows are still open.
"""
import json
import os
import shutil

from gi.repository import GLib, Gtk

from vyom import Plugin as Base
from vyom import ui, util

# keybind: Vyom/power | L | Lock the screen
# keybind: Vyom/power | S | Suspend
# keybind: Vyom/power | E | Log out (after a 5-second countdown)
# keybind: Vyom/power | R | Reboot (after a 5-second countdown)
# keybind: Vyom/power | P | Power off (after a 5-second countdown)
# keybind: Vyom/power | Enter (counting down) | Do it now instead of waiting
# keybind: Vyom/power | Esc (counting down) | Cancel the countdown


def default_logout():
    if os.environ.get("SWAYSOCK") and shutil.which("swaymsg"):
        return "swaymsg exit"
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
        return "hyprctl dispatch exit"
    if os.environ.get("NIRI_SOCKET") and shutil.which("niri"):
        return "niri msg action quit --skip-confirmation"
    return "loginctl terminate-session ${XDG_SESSION_ID:-self}"


ACTIONS = [  # key, letter, label, icon, color, countdown
    ("lock", "L", "Lock", "\U000f033e", "blue", False),
    ("suspend", "S", "Suspend", "\U000f04b2", "teal", False),
    ("logout", "E", "Log out", "\U000f0343", "yellow", True),
    ("reboot", "R", "Reboot", "\U000f0709", "peach", True),
    ("poweroff", "P", "Power off", "\U000f0425", "red", True),
]


def window_count():
    if not shutil.which("swaymsg"):
        return None
    code, out = util.run(["swaymsg", "-t", "get_tree"], timeout=2)
    if code:
        return None
    n = 0

    def walk(node):
        nonlocal n
        if node.get("type") in ("con", "floating_con") and node.get("pid"):
            n += 1
        for c in node.get("nodes", []) + node.get("floating_nodes", []):
            walk(c)
    try:
        walk(json.loads(out))
    except ValueError:
        return None
    return n


class Plugin(Base):
    name, title, icon, color = "vishram", "Power", "⏻", "red"
    layout = "card"
    width = 600

    def __init__(self, vyom, conf):
        super().__init__(vyom, conf)
        self.timer = None
        self.pending = None
        self.left = 0

    def command(self, key):
        defaults = {"lock": "loginctl lock-session", "suspend": "systemctl suspend", "logout": default_logout(),
                    "reboot": "systemctl reboot", "poweroff": "systemctl poweroff"}
        return self.conf.get(key, defaults[key])

    def build_card(self):
        self.cancel()
        import time
        h = time.localtime().tm_hour
        hello = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"
        try:
            up = float(open("/proc/uptime").read().split()[0])
            upt = f"up {int(up // 3600)} h {int(up % 3600 // 60)} min"
        except OSError:
            upt = ""
        n = window_count()
        sub = " · ".join(x for x in (upt, f"{n} window{'s' if n != 1 else ''} open" if n else "") if x)
        user = os.environ.get("USER", "").capitalize()
        head = ui.hbox(ui.vbox(ui.label(f"{hello}{', ' + user if user else ''}", "card-title", xalign=0),
                               ui.label(sub, "card-sub", xalign=0), spacing=2, cls=None),
                       ui.label(time.strftime("%H:%M"), "vishram-clock", hexpand=True, halign=Gtk.Align.END),
                       spacing=10)
        grid = Gtk.Box(spacing=10, homogeneous=True)
        self.buttons = {}
        for key, letter, label, icon, color, _ in ACTIONS:
            b = Gtk.Button()
            b.add_css_class("vishram-btn")
            b.add_css_class(f"v-{color}")
            inner = ui.vbox(ui.label(icon, "vishram-icon"), ui.label(label, "vishram-label"),
                            ui.label(letter, "vishram-key"), spacing=6)
            b.set_child(inner)
            b.connect("clicked", lambda _b, k=key: self.choose(k))
            self.buttons[key] = b
            grid.append(b)
        self.banner = ui.hbox(ui.label("\U000f0709", "vishram-banner-icon"), ui.label("", "vishram-banner-text",
                                                                                     hexpand=True, xalign=0),
                              ui.button("Cancel  Esc", self.cancel), spacing=10, cls="vishram-banner")
        self.banner_text = self.banner.get_first_child().get_next_sibling()
        self.banner.set_visible(False)
        esc = ui.hint_label("Esc", "close")
        esc.set_hexpand(True)
        esc.set_halign(Gtk.Align.END)
        foot = ui.hbox(*(ui.hint_label(k, w) for k, w in (("L", "lock"), ("S", "suspend"), ("E", "log out"),
                                                          ("R", "reboot"), ("P", "power off"))),
                       esc, spacing=14, cls="vishram-foot")
        card = ui.vbox(head, grid, self.banner, foot, spacing=16, cls="card")
        GLib.idle_add(lambda: (self.buttons["lock"].grab_focus(), False)[1])
        return card

    def choose(self, key):
        spec = next(a for a in ACTIONS if a[0] == key)
        if not spec[5]:
            self.run(key)
            return
        self.pending, self.left = key, int(self.conf.get("countdown", 5))
        self.banner.set_visible(True)
        self.tick()
        if self.timer:
            GLib.source_remove(self.timer)
        self.timer = GLib.timeout_add_seconds(1, self.tick)

    def tick(self):
        if not self.pending:
            return False
        if self.left <= 0:
            key = self.pending
            self.cancel()
            self.run(key)
            return False
        label = next(a[2] for a in ACTIONS if a[0] == self.pending)
        n = window_count()
        extra = f" · {n} window{'s' if n != 1 else ''} still open" if n else ""
        self.banner_text.set_label(f"{label} in {self.left}…{extra}")
        self.left -= 1
        return True

    def cancel(self):
        if self.timer:
            GLib.source_remove(self.timer)
        self.timer, self.pending = None, None
        if hasattr(self, "banner"):
            self.banner.set_visible(False)

    def run(self, key):
        self.close()
        # A beat for the panel to go away first (so a lock screen isn't covered).
        GLib.timeout_add(150, lambda: (util.spawn(self.command(key)), False)[1])

    def closed(self):
        self.cancel()

    def key(self, name, row, mods):
        if self.pending:
            if name == "Escape":
                self.cancel()
                return True
            if name in ("Return", "KP_Enter"):
                key = self.pending
                self.cancel()
                self.run(key)
                return True
            return False
        letters = {a[1].lower(): a[0] for a in ACTIONS}
        if not mods and name.lower() in letters:
            self.choose(letters[name.lower()])
            return True
        return False
