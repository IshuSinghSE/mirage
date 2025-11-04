#!/usr/bin/env python3
"""
GTK3-based tray icon helper for Aurynk, using AyatanaAppIndicator3.
Communicates with the main GTK4 app via a simple local socket (can be extended to D-Bus).
"""
# TODO: Use a C binding to use the libayatana-appindicator-glib (GTK4 compatible)

import gi
import os
import socket
import threading
import sys

gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import AyatanaAppIndicator3 as AppIndicator

APP_ID = "aurynk-indicator"
ICON_NAME = "org.aurynk.aurynk"
SOCKET_PATH = "/tmp/aurynk_tray.sock"

class TrayHelper:
    def __init__(self):
        self.indicator = AppIndicator.Indicator.new(
            APP_ID,
            ICON_NAME,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.menu = self.build_menu()
        self.indicator.set_menu(self.menu)
        self.listen_thread = threading.Thread(target=self.listen_socket, daemon=True)
        self.listen_thread.start()

    def build_menu(self):
        menu = Gtk.Menu()
        self.connect_item = Gtk.MenuItem(label="Connect Device")
        self.connect_item.connect("activate", self.on_connect)
        menu.append(self.connect_item)
        self.disconnect_item = Gtk.MenuItem(label="Disconnect")
        self.disconnect_item.connect("activate", self.on_disconnect)
        menu.append(self.disconnect_item)
        self.mirror_item = Gtk.MenuItem(label="Start Mirroring")
        self.mirror_item.connect("activate", self.on_mirror)
        menu.append(self.mirror_item)
        menu.append(Gtk.SeparatorMenuItem())
        show_item = Gtk.MenuItem(label="Show Window")
        show_item.connect("activate", self.on_show)
        menu.append(show_item)
        quit_item = Gtk.MenuItem(label="Quit Aurynk")
        quit_item.connect("activate", self.on_quit)
        menu.append(quit_item)
        menu.show_all()
        return menu

    def on_connect(self, _):
        self.send_command_to_app("connect")
    def on_disconnect(self, _):
        self.send_command_to_app("disconnect")
    def on_mirror(self, _):
        self.send_command_to_app("mirror")
    def on_show(self, _):
        self.send_command_to_app("show")
    def on_quit(self, _):
        self.send_command_to_app("quit")
        Gtk.main_quit()

    def send_command_to_app(self, command):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(SOCKET_PATH)
                s.sendall(command.encode())
        except Exception as e:
            print(f"[Tray] Could not send command '{command}': {e}")

    def listen_socket(self):
        # Listen for state updates from the main app (optional, for dynamic menu)
        try:
            if os.path.exists(SOCKET_PATH):
                os.unlink(SOCKET_PATH)
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(SOCKET_PATH)
            server.listen(1)
            while True:
                conn, _ = server.accept()
                data = conn.recv(1024)
                if data:
                    msg = data.decode()
                    # Example: update menu based on msg
                    if msg.startswith("connected:"):
                        device = msg.split(":", 1)[1]
                        self.connect_item.set_sensitive(False)
                        self.disconnect_item.set_sensitive(True)
                        self.disconnect_item.set_label(f"Disconnect {device}")
                        self.mirror_item.set_sensitive(True)
                    elif msg == "disconnected":
                        self.connect_item.set_sensitive(True)
                        self.disconnect_item.set_sensitive(False)
                        self.disconnect_item.set_label("Disconnect")
                        self.mirror_item.set_sensitive(False)
                conn.close()
        except Exception as e:
            print(f"[Tray] Socket listen error: {e}")

if __name__ == "__main__":
    TrayHelper()
    Gtk.main()
