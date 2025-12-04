import gi

from aurynk.i18n import _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk


def create_session_group() -> Adw.ExpanderRow:
    """
    Creates a Libadwaita Expander Row for 'Session Options' containing various controls.

    Returns:
        Adw.ExpanderRow: The configured expander row.
    """
    expander = Adw.ExpanderRow()
    expander.set_title(_("Session Options"))
    expander.set_subtitle(_("Configure session behavior"))
    expander.set_icon_name("preferences-system-symbolic")

    # Dummy handler for signals
    def dummy_handler(*args):
        pass

    # Helper to add a switch row
    def add_switch_row(title, subtitle=None):
        row = Adw.ActionRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("notify::active", dummy_handler)

        row.add_suffix(switch)
        row.set_activatable_widget(switch)
        expander.add_row(row)

    # Helper to add an action button row
    def add_button_row(title, icon_name, subtitle=None):
        row = Adw.ActionRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)

        button = Gtk.Button()
        button.set_icon_name(icon_name)
        button.set_valign(Gtk.Align.CENTER)
        button.add_css_class("flat")
        button.connect("clicked", dummy_handler)

        row.add_suffix(button)
        expander.add_row(row)

    # --- Toggles ---
    add_switch_row(_("Forward Audio"))
    add_switch_row(_("Turn Screen Off"))
    add_switch_row(_("Stay Awake"), _("Keep device screen on"))
    add_switch_row(_("Fullscreen"), _("Start in fullscreen mode"))
    add_switch_row(_("Show Touches"), _("Visual feedback for touches"))
    add_switch_row(_("Always on Top"), _("Keep window above others"))
    add_switch_row(_("Record Session"), _("Record mirroring session"))

    # --- Actions ---
    add_button_row(_("Volume Up"), "audio-volume-high-symbolic", _("Increase device volume"))
    add_button_row(_("Volume Down"), "audio-volume-low-symbolic", _("Decrease device volume"))
    add_button_row(_("Take Screenshot"), "camera-photo-symbolic", _("Capture device screen"))

    return expander
