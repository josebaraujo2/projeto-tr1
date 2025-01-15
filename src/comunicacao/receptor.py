import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ReceiverWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Receptor")
        self.set_default_size(400, 300)
        
        # Box principal
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)
        
        # Label de status
        self.status_label = Gtk.Label(label="Aguardando mensagens...")
        self.status_label.set_margin_top(10)
        box.pack_start(self.status_label, False, False, 0)
        
        # Campo de texto para mensagens recebidas
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)  # Somente leitura
        self.text_view.set_margin_start(10)
        self.text_view.set_margin_end(10)
        self.text_view.set_margin_top(10)
        self.text_view.set_margin_bottom(10)
        box.pack_start(self.text_view, True, True, 0)

def main():
    win = ReceiverWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()