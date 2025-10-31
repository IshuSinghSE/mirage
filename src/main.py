import io
import qrcode
from PIL import Image
#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf

Adw.init()

class MirageApp(Adw.Application):

    def __init__(self):
        super().__init__(application_id="com.example.mirage")

    def do_activate(self):
        # Load the GResource so the icon is available
        resource = Gio.Resource.load("data/mirage.gresource")
        Gio.Resource._register(resource)
        win = Adw.ApplicationWindow(application=self, title="Mirage")
        win.set_icon_name("com.yourdomain.mirage")
        win.set_default_size(700, 520)

        # --- Header Bar ---
        header_bar = Adw.HeaderBar()
        header_bar.set_show_end_title_buttons(True)

        # App icon and name
        icon = Gtk.Image.new_from_icon_name("com.yourdomain.mirage")
        icon.set_pixel_size(28)
        app_label = Gtk.Label(label="Mirage")
        app_label.set_margin_start(0)
        app_label.set_margin_end(12)
        app_label.set_xalign(0)
        app_label.set_valign(Gtk.Align.CENTER)

        # Search entry (placeholder, not functional yet)
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Search")
        search_entry.set_margin_end(12)
        search_entry.set_hexpand(True)

        # Add Device button
        add_btn = Gtk.Button()
        add_btn.set_label("Add Device")
        add_btn.set_margin_end(6)
        add_btn.set_valign(Gtk.Align.CENTER)
        add_btn.set_icon_name("list-add-symbolic")

        def on_add_btn_clicked(button):

            dialog = Gtk.Dialog(title="Pair New Device", transient_for=win, modal=True)
            dialog.set_default_size(420, 420)

            content = dialog.get_content_area()
            content.set_spacing(16)
            content.set_margin_top(24)
            content.set_margin_bottom(24)
            content.set_margin_start(24)
            content.set_margin_end(24)

            # Title
            title = Gtk.Label()
            title.set_markup("<span size='x-large' weight='bold'>How to Pair New Device</span>")
            title.set_halign(Gtk.Align.START)
            content.append(title)

            # Instructions
            instructions = Gtk.Label(label="1. On your phone, go to: Developer Options > Wireless Debugging\n2. Tap 'Pair device with QR code' and scan")
            instructions.set_justify(Gtk.Justification.LEFT)
            instructions.set_halign(Gtk.Align.START)
            content.append(instructions)

            # Generate QR code image (placeholder data for now)
            qr_data = "WIFI:T:ADB;S:mirage;P:12345678;;"  # Replace with actual pairing string
            qr_img = qrcode.make(qr_data)
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG')
            buf.seek(0)

            # Load QR code into Gtk.Image using GdkPixbuf
            loader = Gtk.Image()
            pixbuf_loader = GdkPixbuf.PixbufLoader.new_with_type('png')
            pixbuf_loader.write(buf.getvalue())
            pixbuf_loader.close()
            pixbuf = pixbuf_loader.get_pixbuf()
            loader.set_from_pixbuf(pixbuf)

            qr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            qr_box.set_valign(Gtk.Align.CENTER)
            qr_box.set_halign(Gtk.Align.CENTER)
            loader.set_pixel_size(180) if hasattr(loader, 'set_pixel_size') else None
            qr_box.append(loader)
            content.append(qr_box)

            # Spinner and status
            spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            spinner_box.set_halign(Gtk.Align.CENTER)
            spinner = Gtk.Spinner()
            spinner.start()
            spinner_box.append(spinner)
            status = Gtk.Label(label="Waiting for connection...")
            status.set_halign(Gtk.Align.CENTER)
            spinner_box.append(status)
            content.append(spinner_box)

            # Cancel button
            cancel_btn = dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)

            def on_response(dialog, response):
                dialog.destroy()

            dialog.connect("response", on_response)
            dialog.show()
            dialog.present()

        add_btn.connect("clicked", on_add_btn_clicked)

        # Header bar layout
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header_box.append(icon)
        header_box.append(app_label)
        header_box.append(search_entry)
        header_box.append(add_btn)
        header_bar.set_title_widget(header_box)

        # --- Main Content ---
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.append(header_bar)

        # Welcome state (centered)
        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        welcome_box.set_vexpand(True)
        welcome_box.set_hexpand(True)
        welcome_box.set_valign(Gtk.Align.CENTER)
        welcome_box.set_halign(Gtk.Align.CENTER)

        # Large phone icon (placeholder)
        phone_icon = Gtk.Image.new_from_icon_name("com.yourdomain.mirage")
        phone_icon.set_pixel_size(96)
        welcome_box.append(phone_icon)

        # Title
        welcome_title = Gtk.Label()
        welcome_title.set_markup("<span size='xx-large' weight='bold'>Connect Your First Device</span>")
        welcome_title.set_justify(Gtk.Justification.CENTER)
        welcome_box.append(welcome_title)

        # Subtitle
        welcome_sub = Gtk.Label(label="Get started by connecting a phone via USB or clicking 'Add Device' to pair wirelessly.")
        welcome_sub.set_justify(Gtk.Justification.CENTER)
        welcome_box.append(welcome_sub)

        main_box.append(welcome_box)

        win.set_content(main_box)
        win.present()

def main(argv):
    app = MirageApp()
    return app.run(argv)

if __name__ == "__main__":
    sys.exit(main(sys.argv))