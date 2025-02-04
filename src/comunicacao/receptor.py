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

import logging
from io import StringIO

class Receptor:
    def __init__(self, simulator, socket_connection):
        self.simulator = simulator
        self.socket_connection = socket_connection
        self.window = ReceiverWindow(self)

        # Configurar o logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Criar um StringIO para capturar os logs
        self.log_capture_string = StringIO()

        # Configurar um handler para enviar os logs para o StringIO
        handler = logging.StreamHandler(self.log_capture_string)
        handler.setLevel(logging.INFO)

        # Formatar as mensagens de log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Adicionar o handler ao logger
        self.logger.addHandler(handler)

    def receive_message(self, received_data, modulacao='NRZ-Polar', enquadramento='Contagem', metodo_erro='Hamming (Correção)'):
        try:
            print("\n=== Iniciando decodificação ===")
            if isinstance(received_data, str):
                received_data = received_data.encode('ascii')
            
            # Limpar o buffer antes de decodificar uma nova mensagem
            self.log_capture_string.truncate(0)  # Limpa o buffer
            self.log_capture_string.seek(0)      # Reinicia o ponteiro do buffer

            # Passar o logger para a função decode_message
            decoded_message = decode_message(
                received_data, 
                modulacao, 
                enquadramento, 
                metodo_erro, 
                "1101", 
                logger=self.logger  # Passando o logger como argumento
            )
            if decoded_message:
                GLib.idle_add(
                    self.window.update_received_message, 
                    decoded_message,
                    received_data,  # Passar o sinal recebido
                    modulacao,      # Passar o tipo de modulação
                    metodo_erro
                )
                return True
            else:
            # Exibir mensagem de erro na interface
                GLib.idle_add(  
                self.window.show_error_message,
                "Erro na mensagem!"
                )
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
        self.error_label = Gtk.Label(label="")
        self.error_label.set_visible(False)
        box.pack_start(self.error_label, False, False, 0)

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

    def update_received_message(self, decoded_message, raw_data, modulacao, metodo_erro):
        """Atualiza a interface para exibir apenas a mensagem limpa"""
        buffer = self.text_view.get_buffer()
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if decoded_message is None:
            self.show_error("Erro na transmissão! Mensagem corrompida.")
        else:
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
            self.last_metodo_erro = metodo_erro
            self.last_message = decoded_message
    
    def show_error_message(self, message):
        self.error_label.set_text(message)
        self.error_label.set_visible(True)
        GLib.timeout_add_seconds(5, self.hide_error)  # Oculta após 5 segundos

    def hide_error(self):
        self.error_label.set_visible(False)
        return False

    def on_view_clicked(self, widget):
        """Abre uma janela de debug para exibir os logs da decodificação"""
        # Verificar se os dados de sinal foram recebidos corretamente
        if self.last_received_signal is not None and len(self.last_received_signal) > 0:
            # Modulação e enquadramento devem ser conhecidos
            modulacao = self.last_modulation_type  # Tipo de modulação
            enquadramento = 'Contagem'  # Método de enquadramento (ajuste conforme necessário)
            metodo_erro = self.last_metodo_erro

            # Chamar a função de decodificação
            decoded_message = decode_message(self.last_received_signal, modulacao, enquadramento, metodo_erro, "1101")
            
            # Se a decodificação for bem-sucedida, exibir os logs de debug
            if decoded_message:
                self.show_debug_window(modulacao, decoded_message)
        else:
            print("Nenhum sinal recebido para visualização.")

    def show_debug_window(self, modulacao, decoded_message):
        # Capturar os logs gerados
        logs = self.receptor.log_capture_string.getvalue()  # Obtém todos os logs capturados

        # Limpar o buffer após capturar os logs
        self.receptor.log_capture_string.truncate(0)  # Limpa o buffer
        self.receptor.log_capture_string.seek(0)      # Reinicia o ponteiro do buffer

        # Exibir os logs na janela de debug
        debug_window = Gtk.Window(title="Debug - Etapas da Decodificação")
        debug_window.set_default_size(600, 400)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        debug_window.add(box)

        buffer = Gtk.TextBuffer()
        text_view = Gtk.TextView(buffer=buffer)
        text_view.set_editable(False)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(text_view)
        box.pack_start(scrolled_window, True, True, 0)

        buffer.set_text(logs)  # Exibe os logs capturados
        debug_window.show_all()