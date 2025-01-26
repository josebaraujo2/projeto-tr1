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

class Receptor:
    def __init__(self, simulator, socket_connection):
        self.simulator = simulator
        self.socket_connection = socket_connection
        self.window = ReceiverWindow(self)

    def receive_message(self, received_data, modulacao='NRZ-Polar', enquadramento='Contagem'):
        try:
            print("\n=== Iniciando decodificação ===")
            decoded_message = decode_message(received_data, modulacao, enquadramento, "CRC", "1101")
            if decoded_message:
                GLib.idle_add(self.window.update_received_message, decoded_message)
                return True  
            return False
        except Exception as e:
            print(f"Erro na recepção: {e}")
            return False

class ReceiverWindow(Gtk.Window):
    def __init__(self, receptor):
        super().__init__(title="Receptor")
        self.receptor = receptor
        self.set_default_size(400, 300)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)

        self.status_label = Gtk.Label(label="Aguardando mensagens...")
        self.status_label.set_margin_top(10)
        box.pack_start(self.status_label, False, False, 0)

        # Usar ScrolledWindow para mensagens longas
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolled, True, True, 0)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_margin_start(10)
        self.text_view.set_margin_end(10)
        self.text_view.set_margin_top(10)
        self.text_view.set_margin_bottom(10)
        scrolled.add(self.text_view)

    def update_received_message(self, message):
        buffer = self.text_view.get_buffer()
        # Adicionar timestamp para cada mensagem
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Adicionar nova mensagem ao final do buffer
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, formatted_message)
        
        # Auto-scroll para a última mensagem
        mark = buffer.create_mark(None, buffer.get_end_iter(), False)
        self.text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        
        # Atualizar status
        self.status_label.set_text(f"Última mensagem recebida às {timestamp}")
        return False  # Importante para o GLib.idle_add