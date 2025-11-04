#!/usr/bin/env python3
"""Main application class for Aurynk."""

import socket
import subprocess
import sys
import os
import gi
import time

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from aurynk.windows.main_window import AurynkWindow


def start_tray_helper():
    """Start the tray helper process if not already running."""
    socket_path = "/tmp/aurynk_tray.sock"
    # Try to connect to the tray helper; if successful, reuse it
    if os.path.exists(socket_path):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(socket_path)
            print("[AurynkApp] Tray helper already running. Reusing existing instance.")
            return True
        except Exception:
            # Socket exists but not connectable: remove and start new helper
            try:
                os.unlink(socket_path)
                print("[AurynkApp] Removed stale tray socket.")
            except Exception as e:
                print(f"[AurynkApp] Could not remove stale tray socket: {e}")
    # Start new tray helper
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "scripts", "aurynk_tray.py")
    )
    subprocess.Popen(["python3", script_path])
    print("[AurynkApp] Started tray helper.")
    return True


class AurynkApp(Adw.Application):
    """Main application class."""

    def __init__(self):
        super().__init__(
            application_id="com.aurynk.aurynk",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_startup(self):
        """Called once when the application starts."""
        Adw.Application.do_startup(self)
        self._load_gresource()
        # print("ENV for tray helper:", os.environ)
        res = start_tray_helper()
        print("[AurynkApp] Startup complete. Res:", res)

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
                    from gi.repository import Gtk, Gdk

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
        SOCKET_PATH = "/tmp/aurynk_tray.sock"
        for attempt in range(5):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(SOCKET_PATH)
                    s.sendall(command.encode())
                return
            except FileNotFoundError:
                time.sleep(0.5)  # Wait for the tray helper to start
            except Exception as e:
                print(f"[AurynkApp] Could not send tray command '{command}': {e}")
                return
        print(f"[AurynkApp] Tray helper socket not available after retries.")

    # Example usage:
    # self.send_tray_command("connected:Redmi Note 14 5G")
    # self.send_tray_command("disconnected")
    # self.send_tray_command("quit")


def main(argv):
    """Main entry point for the application."""
    app = AurynkApp()
    return app.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
