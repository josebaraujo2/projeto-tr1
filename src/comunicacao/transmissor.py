import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class TransmitterWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Transmissor")
        self.set_default_size(400, 300)
        
        # Box principal
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)
        
        # Campo de texto
        self.text_input = Gtk.TextView()
        self.text_input.set_margin_start(10)
        self.text_input.set_margin_end(10)
        self.text_input.set_margin_top(10)
        box.pack_start(self.text_input, True, True, 0)
        
        # Botão de enviar
        send_button = Gtk.Button(label="Transmitir")
        send_button.connect("clicked", self.on_send_clicked)
        send_button.set_margin_start(10)
        send_button.set_margin_end(10)
        send_button.set_margin_bottom(10)
        box.pack_start(send_button, False, False, 0)
    
    def on_send_clicked(self, widget):
        buffer = self.text_input.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        print(f"Transmitindo: {text}")

def main():
    win = TransmitterWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()