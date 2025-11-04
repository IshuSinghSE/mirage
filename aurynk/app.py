#!/usr/bin/env python3
import os
import socket
import subprocess
import sys
import threading
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib

from aurynk.windows.main_window import AurynkWindow


def start_tray_helper():
    """Start the tray helper process if not already running."""
    tray_socket = "/tmp/aurynk_tray.sock"
    # Only reuse the tray helper if the tray socket exists and is connectable
    if os.path.exists(tray_socket):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(tray_socket)
            print("[AurynkApp] Tray helper already running. Reusing existing instance.")
            return True
        except Exception:
            try:
                os.unlink(tray_socket)
                print("[AurynkApp] Removed stale tray socket.")
            except Exception as e:
                print(f"[AurynkApp] Could not remove stale tray socket: {e}")
    # Start new tray helper
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "scripts", "aurynk_tray.py")
    )
    subprocess.Popen(["python3", script_path])


class AurynkApp(Adw.Application):
    """Main application class."""

    def __init__(self):
        super().__init__(
            application_id="com.aurynk.aurynk",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

        # Start tray command listener thread
        self.tray_listener_thread = threading.Thread(target=self.tray_command_listener, daemon=True)
        self.tray_listener_thread.start()

    def tray_command_listener(self):
        """Listen for commands from the tray helper (e.g., show, quit, pair_new)."""
        APP_SOCKET = "/tmp/aurynk_app.sock"
        # Remove stale socket if exists
        if os.path.exists(APP_SOCKET):
            try:
                os.unlink(APP_SOCKET)
            except Exception:
                pass
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(APP_SOCKET)
        server.listen(1)
        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(1024)
                if data:
                    msg = data.decode()
                    if msg == "show":
                        GLib.idle_add(self.present_main_window)
                    elif msg == "pair_new":
                        GLib.idle_add(self.show_pair_dialog)
                    elif msg == "quit":
                        print("[AurynkApp] Received quit from tray. Exiting.")
                        GLib.idle_add(self.quit)
                conn.close()
            except Exception as e:
                print(f"[AurynkApp] Tray command listener error: {e}")

    def show_pair_dialog(self):
        # Show main window and open pairing dialog
        win = self.props.active_window
        if not win:
            win = AurynkWindow(application=self)
        win.present()
        # Try to call a method to show the pairing dialog if it exists
        if hasattr(win, "show_pairing_dialog"):
            win.show_pairing_dialog()
        else:
            print("[AurynkApp] Pairing dialog method not implemented in AurynkWindow.")

    def present_main_window(self):
        win = self.props.active_window
        if not win:
            win = AurynkWindow(application=self)
        win.present()

    def do_startup(self):
        """Called once when the application starts."""
        Adw.Application.do_startup(self)
        self._load_gresource()
        start_tray_helper()

    def do_activate(self):
        """Called when the application is activated (main entry point)."""
        # Get or create the main window
        win = self.props.active_window
        if not win:
            win = AurynkWindow(application=self)
        win.present()

    def _load_gresource(self):
        """Load the compiled GResource file."""
        resource = None
        candidates = [
            # Running from source (development)
            os.path.join(os.getcwd(), "data", "com.aurynk.aurynk.gresource"),
            os.path.join(os.path.dirname(__file__), "..", "data", "com.aurynk.aurynk.gresource"),
            # Installed system-wide
            "/usr/share/aurynk/com.aurynk.aurynk.gresource",
            # Flatpak installation
            "/app/share/aurynk/com.aurynk.aurynk.gresource",
        ]

        for path in candidates:
            try:
                if path and os.path.exists(path):
                    resource = Gio.Resource.load(path)
                    Gio.Resource._register(resource)
                    from gi.repository import Gdk, Gtk

                    Gtk.IconTheme.get_for_display(Gdk.Display.get_default()).add_resource_path(
                        "/com/aurynk/aurynk/icons"
                    )
                    print(f"✓ Loaded GResource from: {path}")
                    break

            except Exception as e:
                print(f"✗ Failed to load GResource from {path}: {e}")

        if resource is None:
            print("⚠ Warning: Could not load GResource file. Some assets may be missing.")

    # --- Tray Helper Communication ---

    def send_tray_command(self, command: str):
        """Send a command to the tray helper process via Unix socket."""
        TRAY_SOCKET = "/tmp/aurynk_tray.sock"
        for attempt in range(5):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(TRAY_SOCKET)
                    s.sendall(command.encode())
                return
            except FileNotFoundError:
                time.sleep(0.5)  # Wait for the tray helper to start
            except Exception as e:
                print(f"[AurynkApp] Could not send tray command '{command}': {e}")
                return
        print("[AurynkApp] Tray helper socket not available after retries.")

    def send_status_to_tray(self, status: str):
        """Send a status update to the tray helper via its socket."""
        TRAY_SOCKET = "/tmp/aurynk_tray.sock"
        for attempt in range(5):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(TRAY_SOCKET)
                    s.sendall(status.encode())
                return
            except FileNotFoundError:
                time.sleep(0.5)
            except Exception as e:
                print(f"[AurynkApp] Could not send tray status '{status}': {e}")
                return
        print("[AurynkApp] Tray helper socket not available after retries.")

    # Example usage:
    # self.send_tray_command("quit")
    # self.send_status_to_tray("connected:Redmi Note 14 5G")
    # self.send_status_to_tray("disconnected")


def main(argv):
    """Main entry point for the application."""
    app = AurynkApp()
    return app.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
