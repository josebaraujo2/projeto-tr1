import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from src.enlace.enquadramento import enquadrar_contagem_caracteres
from src.enlace.detecao_erro import calcular_paridade
from src.fisica.digital import ModulacaoDigital

class Transmissor:
    def __init__(self, simulator, client_socket):  # Adiciona o parâmetro client_socket
        self.simulator = simulator
        self.client_socket = client_socket  # Armazena o socket do cliente
        self.window = TransmitterWindow(self)

    def transmit_message(self, message):
        #Implementar
        return

class TransmitterWindow(Gtk.Window):
    def __init__(self, transmissor):
        super().__init__(title="Transmissor")
        self.transmissor = transmissor
        self.set_default_size(400, 300)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)
        
        self.text_input = Gtk.TextView()
        self.text_input.set_margin_start(10)
        self.text_input.set_margin_end(10)
        self.text_input.set_margin_top(10)
        box.pack_start(self.text_input, True, True, 0)
        
        send_button = Gtk.Button(label="Transmitir")
        send_button.connect("clicked", self.on_send_clicked)
        send_button.set_margin_start(10)
        send_button.set_margin_end(10)
        send_button.set_margin_bottom(10)
        box.pack_start(send_button, False, False, 0)
    
    def on_send_clicked(self, widget):
        buffer = self.text_input.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        self.transmissor.transmit_message(text)