import gi
import socket
import threading
import random
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from correcao_erro import corrigir_hamming


class ReceptorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Receptor - Código de Hamming")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Layout
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.add(grid)

        # Bits recebidos
        self.received_label = Gtk.Label(label="Bits recebidos:")
        grid.attach(self.received_label, 0, 0, 1, 1)
        self.received_entry = Gtk.Entry(editable=False)
        grid.attach(self.received_entry, 1, 0, 2, 1)

        # Botão para introduzir erro
        self.error_button = Gtk.Button(label="Introduzir Erro")
        self.error_button.connect("clicked", self.on_introduce_error)
        grid.attach(self.error_button, 0, 1, 3, 1)

        # Bits com erro
        self.error_label = Gtk.Label(label="Bits com erro:")
        grid.attach(self.error_label, 0, 2, 1, 1)
        self.error_entry = Gtk.Entry(editable=False)
        grid.attach(self.error_entry, 1, 2, 2, 1)

        # Botão para corrigir erro
        self.correct_button = Gtk.Button(label="Corrigir Erro")
        self.correct_button.connect("clicked", self.on_correct_error)
        grid.attach(self.correct_button, 0, 3, 3, 1)

        # Bits corrigidos
        self.correct_label = Gtk.Label(label="Bits corrigidos:")
        grid.attach(self.correct_label, 0, 4, 1, 1)
        self.correct_entry = Gtk.Entry(editable=False)
        grid.attach(self.correct_entry, 1, 4, 2, 1)

        # Variáveis internas
        self.received_bits = ""
        self.error_bits = ""

        # Iniciar thread do servidor
        threading.Thread(target=self.start_server, daemon=True).start()

    def start_server(self):
        # Criar servidor socket local
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 65432))
            s.listen()
            while True:
                conn, _ = s.accept()
                with conn:
                    self.received_bits = conn.recv(1024).decode('utf-8')
                    self.received_entry.set_text(self.received_bits)

    def on_introduce_error(self, widget):
        if not self.received_bits:
            self.error_entry.set_text("Nenhum bit recebido.")
            return
        bits = list(self.received_bits)
        error_pos = random.randint(0, len(bits) - 1)
        bits[error_pos] = '1' if bits[error_pos] == '0' else '0'
        self.error_bits = ''.join(bits)
        self.error_entry.set_text(self.error_bits)

    def on_correct_error(self, widget):
        if not self.error_bits:
            self.correct_entry.set_text("Nenhum erro introduzido.")
            return
        corrected_bits = corrigir_hamming(self.error_bits)
        self.correct_entry.set_text(corrected_bits)


def main():
    app = ReceptorApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
