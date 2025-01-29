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

class Receptor:
    def __init__(self, simulator, socket_connection):
        self.simulator = simulator
        self.socket_connection = socket_connection
        self.window = ReceiverWindow(self)

    def receive_message(self, received_data, modulacao='NRZ-Polar', enquadramento='Contagem'):
        try:
            print("\n=== Iniciando decodificação ===")
            if isinstance(received_data, str):
                received_data = received_data.encode('ascii')
            
            decoded_message = decode_message(received_data, modulacao, enquadramento, "CRC", "1101")
            if decoded_message:
                GLib.idle_add(
                    self.window.update_received_message, 
                    decoded_message,
                    received_data,  # Passar o sinal recebido
                    modulacao      # Passar o tipo de modulação
                )
            return True
        
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

        # Status label
        self.status_label = Gtk.Label(label="Aguardando mensagens...")
        self.status_label.set_margin_top(10)
        box.pack_start(self.status_label, False, False, 0)

        # ScrolledWindow para mensagens
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

        # Botão de visualizar demodulação
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_start(10)
        button_box.set_margin_end(10)
        button_box.set_margin_bottom(10)
        box.pack_start(button_box, False, False, 0)

        view_demod_button = Gtk.Button(label="Visualizar Demodulação")
        view_demod_button.connect("clicked", self.on_view_clicked)
        button_box.pack_start(view_demod_button, True, True, 0)

        # Armazenar o último sinal recebido e modulação
        self.last_received_signal = None
        self.last_modulation_type = None
        self.last_message = None

    def update_received_message(self, decoded_message, raw_data, modulacao):
        """Atualiza a interface para exibir apenas a mensagem limpa"""
        buffer = self.text_view.get_buffer()
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Exibir a mensagem limpa recebida
        formatted_message = f"[{timestamp}] {decoded_message}\n"
        buffer.insert(buffer.get_end_iter(), formatted_message)
        mark = buffer.create_mark(None, buffer.get_end_iter(), False)
        self.text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

        # Atualizar o status da última mensagem recebida
        self.status_label.set_text(f"Última mensagem recebida às {timestamp}")
        
        # Salvar os dados recebidos para visualização futura
        self.last_received_signal = raw_data
        self.last_modulation_type = modulacao
        self.last_message = decoded_message
        
        # Mostrar um pop-up de sucesso (se não houver erro)
        self.show_success_popup(decoded_message)

    def show_success_popup(self, message):
        """Exibe um popup indicando que a mensagem foi recebida com sucesso"""
        dialog = Gtk.MessageDialog(
            self, 
            Gtk.DialogFlags.MODAL, 
            Gtk.MessageType.INFO, 
            Gtk.ButtonsType.OK, 
            f"Mensagem sem erros"
        )
        dialog.run()
        dialog.destroy()

    def on_view_clicked(self, widget):
        """Abre uma janela de debug para exibir os logs da decodificação"""
        # Verificar se os dados de sinal foram recebidos corretamente
        if self.last_received_signal is not None and len(self.last_received_signal) > 0:
            # Modulação e enquadramento devem ser conhecidos
            modulacao = self.last_modulation_type  # Tipo de modulação
            enquadramento = 'Contagem'  # Método de enquadramento (ajuste conforme necessário)

            # Chamar a função de decodificação
            decoded_message = decode_message(self.last_received_signal, modulacao, enquadramento, "CRC", "1101")
            
            # Se a decodificação for bem-sucedida, exibir os logs de debug
            if decoded_message:
                self.show_debug_window(modulacao, decoded_message)
        else:
            print("Nenhum sinal recebido para visualização.")

    def show_debug_window(self, modulacao, decoded_message):
        """Exibe a janela de debug com as etapas de decodificação"""
        # Criar uma nova janela para exibir os logs
        debug_window = Gtk.Window(title="Debug - Etapas da Decodificação")
        debug_window.set_default_size(600, 400)

        # Box para organizar a interface
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        debug_window.add(box)

        # Exibir logs
        buffer = Gtk.TextBuffer()
        text_view = Gtk.TextView(buffer=buffer)
        text_view.set_editable(False)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(text_view)
        box.pack_start(scrolled_window, True, True, 0)

        # Formatando os logs com as etapas de decodificação
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Adicionando logs de cada etapa da decodificação
        log_message = f"[{timestamp}] Dados recebidos (raw): {self.last_received_signal}\n"
        log_message += f"[{timestamp}] Modulação: {modulacao}\n"

        # Demodulação (após a modulação)
        log_message += f"[{timestamp}] Bits demodulados: {''.join(map(str, decoded_message))}\n"

        # Mensagem desenquadrada (adicionando o método de desenquadramento selecionado)
        log_message += f"[{timestamp}] Mensagem desenquadrada: {decoded_message}\n"

        # Exibindo no buffer da janela de debug
        buffer.set_text(log_message)

        # Exibindo a janela
        debug_window.show_all()
