import gi
import socket
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from correcao_erro import gerar_hamming


class TransmissorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Transmissor - Código de Hamming")
        self.set_border_width(10)
        self.set_default_size(400, 200)
        
        # Layout
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.add(grid)

        # Entrada de bits
        self.input_label = Gtk.Label(label="Bits de entrada:")
        grid.attach(self.input_label, 0, 0, 1, 1)
        self.input_entry = Gtk.Entry()
        grid.attach(self.input_entry, 1, 0, 2, 1)

        # Botão para gerar Hamming
        self.generate_button = Gtk.Button(label="Gerar e Enviar")
        self.generate_button.connect("clicked", self.on_generate_and_send)
        grid.attach(self.generate_button, 0, 1, 3, 1)

        # Resultado dos bits Hamming
        self.result_label = Gtk.Label(label="Bits Hamming gerados:")
        grid.attach(self.result_label, 0, 2, 1, 1)
        self.result_entry = Gtk.Entry(editable=False)
        grid.attach(self.result_entry, 1, 2, 2, 1)

    def on_generate_and_send(self, widget):
        input_bits = self.input_entry.get_text().strip()
        if not all(bit in "01" for bit in input_bits):
            self.result_entry.set_text("Entrada inválida. Use apenas 0 e 1.")
            return
        hamming_bits = gerar_hamming(input_bits)
        self.result_entry.set_text(hamming_bits)
        self.send_to_receptor(hamming_bits)

    def send_to_receptor(self, hamming_bits):
        try:
            # Simular envio para receptor via socket local
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 65432))
                s.sendall(hamming_bits.encode('utf-8'))
        except ConnectionRefusedError:
            self.result_entry.set_text("Receptor não encontrado.")


def main():
    app = TransmissorApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
