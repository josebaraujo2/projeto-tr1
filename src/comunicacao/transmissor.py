import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from src.enlace.enquadramento import (
    enquadrar_contagem_caracteres, 
    enquadrar_insercao_bytes,
    desenquadrar_contagem_caracteres, 
    desenquadrar_insercao_bytes
)
from src.enlace.detecao_erro import calcular_paridade, verificar_paridade
from src.fisica.digital import ModulacaoDigital
from src.comunicacao.test_network_simulator import encode_message, decode_message
from src.comunicacao.visualizacao_de_sinal import SignalVisualizationWindow

class Transmissor:
    def __init__(self, simulator, client_socket):
        self.simulator = simulator
        self.client_socket = client_socket
        self.window = TransmitterWindow(self)

    def transmit_message(self, message, modulacao='NRZ-Polar', enquadramento='Contagem'):
        try:
            import pickle
            import struct
            
            # Preparar e enviar o header
            header = {
                'modulacao': modulacao,
                'enquadramento': enquadramento
            }
            header_data = pickle.dumps(header)
            header_size = struct.pack('>I', len(header_data))
            self.client_socket.send(header_size)
            self.client_socket.send(header_data)
            
            # Preparar e enviar a mensagem modulada
            modulated_message = encode_message(message, modulacao, enquadramento, "CRC", "1101")
            data = pickle.dumps(modulated_message)
            data_size = struct.pack('>I', len(data))
            self.client_socket.send(data_size)
            self.client_socket.send(data)
            
            return True
        except Exception as e:
            print(f"Erro na transmissão: {e}")
            return False

class TransmitterWindow(Gtk.Window):
    def __init__(self, transmitter):
        super().__init__(title="Transmissor")
        self.transmitter = transmitter
        self.set_default_size(400, 300)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)

        # Text input (mantido como estava)
        self.text_input = Gtk.TextView()
        self.text_input.set_margin_start(10)
        self.text_input.set_margin_end(10)
        self.text_input.set_margin_top(10)
        box.pack_start(self.text_input, True, True, 0)

        # Modulação Combo (mantido como estava)
        modulacao_label = Gtk.Label(label="Modulação:")
        box.pack_start(modulacao_label, False, False, 0)
        self.modulacao_combo = Gtk.ComboBoxText()
        self.modulacao_combo.append_text('NRZ-Polar')
        self.modulacao_combo.append_text('Manchester')
        self.modulacao_combo.append_text('Bipolar')
        self.modulacao_combo.set_active(0)
        box.pack_start(self.modulacao_combo, False, False, 0)

        # Enquadramento Combo (mantido como estava)
        enquadramento_label = Gtk.Label(label="Enquadramento:")
        box.pack_start(enquadramento_label, False, False, 0)
        self.enquadramento_combo = Gtk.ComboBoxText()
        self.enquadramento_combo.append_text('Contagem')
        self.enquadramento_combo.append_text('Inserção Bytes')
        self.enquadramento_combo.set_active(0)
        box.pack_start(self.enquadramento_combo, False, False, 0)

        # Button box para organizar os botões
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_start(10)
        button_box.set_margin_end(10)
        button_box.set_margin_bottom(10)
        box.pack_start(button_box, False, False, 0)

        # Visualizar button
        view_button = Gtk.Button(label="Visualizar Modulação")
        view_button.connect("clicked", self.on_view_clicked)
        button_box.pack_start(view_button, True, True, 0)

        # Send button
        send_button = Gtk.Button(label="Transmitir")
        send_button.connect("clicked", self.on_send_clicked)
        button_box.pack_start(send_button, True, True, 0)

        # Armazenar último sinal modulado
        self.last_modulated_signal = None

    def on_view_clicked(self, widget):
        if self.last_modulated_signal is not None and self.last_modulated_signal.size > 0:
            # Se não houver sinal modulado, modular o texto atual
            buffer = self.text_input.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            text = buffer.get_text(start_iter, end_iter, True)
            modulacao = self.modulacao_combo.get_active_text()
            
            # Modular o texto
            modulated_signal = encode_message(text, modulacao, 'Contagem', "CRC", "1101")
            self.last_modulated_signal = modulated_signal

        # Criar e mostrar janela de visualização
        vis_window = SignalVisualizationWindow(f"Visualização - {self.modulacao_combo.get_active_text()}")
        vis_window.plot_signal(self.last_modulated_signal, self.modulacao_combo.get_active_text())
        vis_window.show_all()

    def on_send_clicked(self, widget):
        buffer = self.text_input.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, True)

        modulacao = self.modulacao_combo.get_active_text()
        enquadramento = self.enquadramento_combo.get_active_text()

        # Armazenar o sinal modulado antes de enviar
        self.last_modulated_signal = encode_message(text, modulacao, enquadramento, "CRC", "1101")
        self.transmitter.transmit_message(text, modulacao, enquadramento)