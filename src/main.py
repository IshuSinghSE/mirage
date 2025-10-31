#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio

Adw.init()

class MirageApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.mirage")

    def do_activate(self):
        win = Adw.ApplicationWindow(application=self, title="mirage")
        win.set_default_size(480, 240)

        # Create a header bar (without custom window controls)
        header_bar = Adw.HeaderBar()

        # Add a label as the main content
        label = Gtk.Label(label="Hello, Libadwaita! 🎉")
        label.set_margin_top(24)
        label.set_margin_bottom(24)
        label.set_margin_start(24)
        label.set_margin_end(24)

        # Use a box to combine header and content
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.append(header_bar)
        vbox.append(label)

        win.set_content(vbox)
        win.present()

    # Create a header bar (without custom window controls)
    header_bar = Adw.HeaderBar()

    # Add a label as the main content
    label = Gtk.Label(label="Hello, Libadwaita! 🎉")
    label.set_margin_top(24)
    label.set_margin_bottom(24)
    label.set_margin_start(24)
    label.set_margin_end(24)

    # Use a box to combine header and content
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    vbox.append(header_bar)
    vbox.append(label)

def main(argv):
    app = MirageApp()
    return app.run(argv)

if __name__ == "__main__":
    sys.exit(main(sys.argv))