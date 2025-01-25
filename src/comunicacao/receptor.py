import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from src.enlace.enquadramento import desenquadrar_contagem_caracteres
from src.enlace.detecao_erro import verificar_paridade
from src.comunicacao.gerenciador_socket import inject_errors

class Receptor:
    def __init__(self, simulator, socket_connection):
        self.simulator = simulator
        self.socket_connection = socket_connection
        self.window = ReceiverWindow(self)
   
    def receive_message(self):
        #Implementar
        return

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
        
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_margin_start(10)
        self.text_view.set_margin_end(10)
        self.text_view.set_margin_top(10)
        self.text_view.set_margin_bottom(10)
        box.pack_start(self.text_view, True, True, 0)
    
    def update_received_message(self, message):
        buffer = self.text_view.get_buffer()
        buffer.set_text(message)
        self.status_label.set_text("Mensagem recebida!")
    
    def show_error_message(self):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Erro na transmissão"
        )
        dialog.format_secondary_text("Falha na verificação de paridade.")
        dialog.run()
        dialog.destroy()