import gi
gi.require_version("Gtk", "3.0")  # Se usar GTK 4, ajuste aqui
from gi.repository import Gtk, GObject

import socket
import threading

# Importa as funções de enquadramento/desenquadramento
from enquadramento import (
    enquadra_contagem,
    desenquadra_contagem,
    enquadra_insercao,
    desenquadra_insercao
)

class ReceiverWindow(Gtk.Window):
    """
    Janela de Recepção:
    - Abre um socket TCP para escutar em (host, port).
    - Recebe os dados (bytes) e exibe o 'quadro bruto' e a tentativa de desenquadramento.
    - Para simplificar, faremos com que a interface permita escolher o protocolo de desenquadramento
      ou tente ambos e mostre o que der certo.
    """
    def __init__(self):
        super().__init__(title="Receptor (Receiver)")
        self.set_border_width(10)
        
        # Layout principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Campo para escolher a porta
        hbox_port = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_port = Gtk.Label(label="Porta para escutar:")
        self.entry_port = Gtk.Entry()
        self.entry_port.set_text("5000")
        btn_listen = Gtk.Button(label="Iniciar Servidor")
        btn_listen.connect("clicked", self.on_listen_clicked)
        
        hbox_port.pack_start(lbl_port, False, False, 0)
        hbox_port.pack_start(self.entry_port, False, False, 0)
        hbox_port.pack_start(btn_listen, False, False, 0)
        
        vbox.pack_start(hbox_port, False, False, 0)
        
        # ComboBox para escolher protocolo de desenquadramento
        self.combo_protocol = Gtk.ComboBoxText()
        self.combo_protocol.append_text("Contagem")
        self.combo_protocol.append_text("Inserção")
        self.combo_protocol.set_active(0)  # Padrão: Contagem
        vbox.pack_start(self.combo_protocol, False, False, 0)
        
        # Área de texto para mostrar recebimentos
        self.buffer_display = Gtk.TextBuffer()
        textview = Gtk.TextView(buffer=self.buffer_display)
        textview.set_editable(False)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(textview)
        
        vbox.pack_start(scroll, True, True, 0)
        
        # Atributo para thread de servidor
        self.server_thread = None
        self.server_socket = None
        self.stop_server = threading.Event()
        
        self.set_default_size(400, 300)
        self.show_all()

    def on_listen_clicked(self, widget):
        """Inicia a thread de servidor TCP na porta escolhida."""
        port_str = self.entry_port.get_text().strip()
        if not port_str.isdigit():
            self.log_message("Porta inválida.")
            return
        port = int(port_str)
        
        # Se já existe servidor rodando, paramos
        if self.server_thread and self.server_thread.is_alive():
            self.log_message("Servidor já está em execução.")
            return
        
        # Reinicia a flag de parada
        self.stop_server.clear()
        
        self.server_thread = threading.Thread(
            target=self.run_server,
            args=("0.0.0.0", port),
            daemon=True  # thread demon, fecha junto com app
        )
        self.server_thread.start()
        
        self.log_message(f"Servidor iniciado na porta {port}.")

    def run_server(self, host, port):
        """Método que roda em thread separada, escuta TCP e recebe frames."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(5)
            s.settimeout(1.0)  # timeout para poder checar "stop_server" periodicamente
            
            while not self.stop_server.is_set():
                try:
                    client_socket, addr = s.accept()
                except socket.timeout:
                    continue  # volta a checar stop_server
                
                self.log_message_threadsafe(f"Conexão de {addr}.")
                
                # Recebe dados até encerrar a conexão
                with client_socket:
                    data = b""
                    while True:
                        try:
                            chunk = client_socket.recv(1024)
                            if not chunk:
                                break
                            data += chunk
                        except:
                            break
                    
                    if data:
                        # Temos um quadro. Vamos tentar desenquadrar.
                        self.process_received_data(data, addr)

    def process_received_data(self, data: bytes, addr):
        """
        Processa os dados recebidos:
        1. Exibe o quadro bruto (em hexa ou decimal).
        2. Desenquadra conforme o protocolo escolhido no combo.
        3. Mostra o texto resultante ou erro.
        """
        # Exibir quadro bruto
        proto = self.combo_protocol.get_active_text()  # "Contagem" ou "Inserção"
        
        # Log do quadro bruto (hexa)
        self.log_message_threadsafe(f"Quadro bruto (hex): {data.hex()}")
        
        if proto == "Contagem":
            try:
                text = desenquadra_contagem(data)
                self.log_message_threadsafe(f"Texto desenquadrado (Contagem): {text}")
            except Exception as e:
                self.log_message_threadsafe(f"Erro ao desenquadrar (Contagem): {e}")
        else:
            # Inserção
            try:
                text = desenquadra_insercao(data)
                self.log_message_threadsafe(f"Texto desenquadrado (Inserção): {text}")
            except Exception as e:
                self.log_message_threadsafe(f"Erro ao desenquadrar (Inserção): {e}")

    def log_message_threadsafe(self, msg: str):
        """Agendar para atualizar a interface (TextBuffer) na thread principal."""
        GObject.idle_add(self.log_message, msg)

    def log_message(self, msg: str):
        """Escreve 'msg' no TextBuffer de forma simples."""
        end_iter = self.buffer_display.get_end_iter()
        self.buffer_display.insert(end_iter, msg + "\n")

    def close_server(self):
        """Fecha o servidor ao encerrar a janela."""
        self.stop_server.set()
        # Se quiser, podemos fechar o socket forçosamente
        # mas usamos settimeout e "stop_server" no loop

    def destroy(self):
        self.close_server()
        super().destroy()

class TransmitterWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Transmissor (Transmitter)")
        self.set_border_width(10)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Campos IP e Porta
        hbox_net = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        lbl_ip = Gtk.Label(label="IP do Receptor:")
        self.entry_ip = Gtk.Entry()
        self.entry_ip.set_text("127.0.0.1")
        
        lbl_port = Gtk.Label(label="Porta:")
        self.entry_port = Gtk.Entry()
        self.entry_port.set_text("5000")
        
        hbox_net.pack_start(lbl_ip, False, False, 0)
        hbox_net.pack_start(self.entry_ip, True, True, 0)
        hbox_net.pack_start(lbl_port, False, False, 0)
        hbox_net.pack_start(self.entry_port, True, True, 0)
        
        vbox.pack_start(hbox_net, False, False, 0)
        
        # Campo de mensagem
        lbl_msg = Gtk.Label(label="Mensagem a enviar:")
        self.entry_msg = Gtk.Entry()
        self.entry_msg.set_text("Olá, receptor!")
        
        vbox.pack_start(lbl_msg, False, False, 0)
        vbox.pack_start(self.entry_msg, False, False, 0)
        
        # Escolha de protocolo
        self.combo_protocol = Gtk.ComboBoxText()
        self.combo_protocol.append_text("Contagem")
        self.combo_protocol.append_text("Inserção")
        self.combo_protocol.set_active(0)
        
        vbox.pack_start(self.combo_protocol, False, False, 0)
        
        # Botão Enviar
        btn_send = Gtk.Button(label="Enviar")
        btn_send.connect("clicked", self.on_send_clicked)
        vbox.pack_start(btn_send, False, False, 0)
        
        # Área de log/saída
        self.buffer_output = Gtk.TextBuffer()
        textview = Gtk.TextView(buffer=self.buffer_output)
        textview.set_editable(False)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(textview)
        
        vbox.pack_start(scroll, True, True, 0)
        
        self.set_default_size(400, 300)
        self.show_all()
    
    def on_send_clicked(self, widget):
        ip = self.entry_ip.get_text().strip()
        port_str = self.entry_port.get_text().strip()
        msg = self.entry_msg.get_text()
        
        if not port_str.isdigit():
            self.log(f"Porta inválida: {port_str}")
            return
        
        port = int(port_str)
        
        # Escolhe protocolo
        proto = self.combo_protocol.get_active_text()  # "Contagem" ou "Inserção"
        if proto == "Contagem":
            quadro = enquadra_contagem(msg)
        else:
            quadro = enquadra_insercao(msg)
        
        # Tenta enviar via socket TCP
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, port))
                s.sendall(quadro)
            
            self.log(f"Enviado para {ip}:{port} - Quadro (hex): {quadro.hex()}")
        except Exception as e:
            self.log(f"Erro ao enviar: {e}")
    
    def log(self, text: str):
        end_iter = self.buffer_output.get_end_iter()
        self.buffer_output.insert(end_iter, text + "\n")

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Camada de Enlace - Principal")
        self.set_border_width(10)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        lbl_info = Gtk.Label(label="Selecione qual módulo abrir:")
        vbox.pack_start(lbl_info, False, False, 0)
        
        btn_tx = Gtk.Button(label="Abrir Transmissor")
        btn_tx.connect("clicked", self.on_btn_tx)
        vbox.pack_start(btn_tx, False, False, 0)
        
        btn_rx = Gtk.Button(label="Abrir Receptor")
        btn_rx.connect("clicked", self.on_btn_rx)
        vbox.pack_start(btn_rx, False, False, 0)
        
        self.set_default_size(300, 150)
        self.show_all()
    
    def on_btn_tx(self, widget):
        tx_win = TransmitterWindow()
        tx_win.connect("destroy", tx_win.destroy)
        tx_win.show_all()
    
    def on_btn_rx(self, widget):
        rx_win = ReceiverWindow()
        rx_win.connect("destroy", rx_win.destroy)
        rx_win.show_all()

def main():
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
