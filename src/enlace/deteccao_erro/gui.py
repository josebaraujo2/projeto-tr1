import gi
from deteccao_erro import calcular_paridade, verificar_paridade, calcular_crc, verificar_crc

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import socket
import random
import threading

class TransmitterApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Transmissor")

        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Layout principal
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(layout)

        # Entrada de bits
        self.bits_entry = Gtk.Entry()
        self.bits_entry.set_placeholder_text("Digite a sequência de bits (ex: 110101)")
        layout.pack_start(self.bits_entry, False, False, 0)

        # Escolha do protocolo
        self.protocol_combo = Gtk.ComboBoxText()
        self.protocol_combo.append_text("Bit de Paridade Par")
        self.protocol_combo.append_text("CRC (CRC-32, IEEE 802)")
        self.protocol_combo.set_active(0)
        layout.pack_start(self.protocol_combo, False, False, 0)

        # Botão para inserir erro
        self.error_check = Gtk.CheckButton(label="Inserir erro na transmissão")
        layout.pack_start(self.error_check, False, False, 0)

        # Botão de transmitir
        transmit_button = Gtk.Button(label="Transmitir")
        transmit_button.connect("clicked", self.on_transmit_clicked)
        layout.pack_start(transmit_button, False, False, 0)

        # Área de saída
        self.output_label = Gtk.Label()
        self.output_label.set_xalign(0)
        layout.pack_start(self.output_label, False, False, 0)

        # Configuração de socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_host = "127.0.0.1"
        self.receiver_port = 5006

    def on_transmit_clicked(self, button):
        bits = self.bits_entry.get_text()
        protocol = self.protocol_combo.get_active_text()

        if not bits or not all(bit in "01" for bit in bits):
            self.output_label.set_text("Erro: Por favor, insira uma sequência válida de bits.")
            return

        if protocol == "Bit de Paridade Par":
            bits_com_paridade = calcular_paridade(bits)

            if self.error_check.get_active():
                bits_com_paridade = self.introduzir_erro(bits_com_paridade)

            self.socket.sendto(f"PARIDADE:{bits_com_paridade}".encode(), (self.receiver_host, self.receiver_port))

        elif protocol == "CRC (CRC-32, IEEE 802)":
            polinomio = "100000100110000010001110110110111"
            bits_com_crc = calcular_crc(bits, polinomio)

            if self.error_check.get_active():
                bits_com_crc = self.introduzir_erro(bits_com_crc)

            self.socket.sendto(f"CRC:{bits_com_crc}:{polinomio}".encode(), (self.receiver_host, self.receiver_port))

        self.output_label.set_text("Mensagem transmitida para o receptor.")

    def introduzir_erro(self, bits):
        bits = list(bits)
        pos = random.randint(0, len(bits) - 1)
        bits[pos] = '0' if bits[pos] == '1' else '1'
        return ''.join(bits)

class ReceiverApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Receptor")

        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Layout principal
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(layout)

        # Área de saída
        self.output_label = Gtk.Label()
        self.output_label.set_xalign(0)
        layout.pack_start(self.output_label, False, False, 0)

        # Configuração de socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = "127.0.0.1"
        self.port = 5006
        self.socket.bind((self.host, self.port))

        # Thread para escutar mensagens
        threading.Thread(target=self.listen_for_messages, daemon=True).start()

    def listen_for_messages(self):
        while True:
            data, _ = self.socket.recvfrom(1024)
            message = data.decode()

            if message.startswith("PARIDADE:"):
                bits_com_paridade = message.split(":")[1]
                valid = verificar_paridade(bits_com_paridade)
                GLib.idle_add(self.update_output, f"Bits recebidos com paridade: {bits_com_paridade}\n"
                                              f"Integridade: {'Válida' if valid else 'Inválida'}")

            elif message.startswith("CRC:"):
                _, bits_com_crc, polinomio = message.split(":")
                valid = verificar_crc(bits_com_crc, polinomio)
                GLib.idle_add(self.update_output, f"Bits recebidos com CRC: {bits_com_crc}\n"
                                              f"Integridade: {'Válida' if valid else 'Inválida'}")

    def update_output(self, text):
        self.output_label.set_text(text)

def main():
    transmitter = TransmitterApp()
    transmitter.connect("destroy", Gtk.main_quit)
    transmitter.show_all()

    receiver = ReceiverApp()
    receiver.connect("destroy", Gtk.main_quit)
    receiver.show_all()

    Gtk.main()

if __name__ == "__main__":
    main()
