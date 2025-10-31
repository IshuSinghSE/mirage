import io
import qrcode
from gi.repository import Gtk, GdkPixbuf

def create_qr_widget(qr_string, size=180):
    """
    Returns a Gtk.Box containing a QR code image for the given string.
    """
    qr_img = qrcode.make(qr_string)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    loader = Gtk.Image()
    pixbuf_loader = GdkPixbuf.PixbufLoader.new_with_type('png')
    pixbuf_loader.write(buf.getvalue())
    pixbuf_loader.close()
    pixbuf = pixbuf_loader.get_pixbuf()
    loader.set_from_pixbuf(pixbuf)
    if hasattr(loader, 'set_pixel_size'):
        loader.set_pixel_size(size)
    qr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    qr_box.set_valign(Gtk.Align.CENTER)
    qr_box.set_halign(Gtk.Align.CENTER)
    qr_box.append(loader)
    return qr_box
