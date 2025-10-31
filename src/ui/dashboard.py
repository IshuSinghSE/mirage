
# Required imports
from gi.repository import Gtk, Adw

def build_dashboard_window(app, win):
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

    # Add Device button (callback to be set by caller)
    add_btn = Gtk.Button()
    add_btn.set_label("Add Device")
    add_btn.set_margin_end(6)
    add_btn.set_valign(Gtk.Align.CENTER)
    add_btn.set_icon_name("list-add-symbolic")

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
    return add_btn
