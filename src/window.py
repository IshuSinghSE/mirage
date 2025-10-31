# Minimal window module for scrcpy-dashboard
from gi.repository import Adw, Gtk

def create_main_window(application):
    win = Adw.ApplicationWindow(application=application, title="scrcpy-dashboard")
    win.set_default_size(800, 480)
    label = Gtk.Label(label="scrcpy-dashboard")
    win.set_content(label)
    return win
