import gi
gi.require_version("Gtk", "3.0")  # ou "4.0" se você estiver usando GTK4
from gi.repository import Gtk, GObject

import socket
import threading

from src.enlace.enquadramento import (
    enquadrar_contagem_caracteres,
    desenquadrar_contagem_caracteres,
    enquadrar_insercao_bytes,
    desenquadrar_insercao_bytes
)

# ------------------------------------------------------------
# Funções auxiliares para bits <-> ASCII
# ------------------------------------------------------------
def bits_to_ascii(bitstring: str) -> bytes:
    """ Converte string de bits (ex '010101') em bytes ASCII para envio. """
    return bitstring.encode('ascii')

def ascii_to_bits(ascii_data: bytes) -> str:
    """ Converte bytes ASCII para string de bits. Ex: b'010101' -> '010101'. """
    return ascii_data.decode('ascii')


# ------------------------------------------------------------
# Janela do Receptor
# ------------------------------------------------------------
class ReceiverWindow(Gtk.Window):
    """
    Recebe dados via socket TCP.
    - Escolhe protocolo (bits ou bytes).
    - Ao chegar dados, exibe:
      - O quadro bruto (em bits se for contagem, ou em hex se for inserção).
      - O resultado desenquadrado.
    """
    def __init__(self):
        super().__init__(title="Receptor (Simulação)")
        self.set_border_width(10)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Linha para porta e botão iniciar servidor
        hbox_port = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_port = Gtk.Label(label="Porta:")
        self.entry_port = Gtk.Entry()
        self.entry_port.set_text("5000")
        btn_listen = Gtk.Button(label="Iniciar Servidor")
        btn_listen.connect("clicked", self.on_listen_clicked)
        hbox_port.pack_start(lbl_port, False, False, 0)
        hbox_port.pack_start(self.entry_port, False, False, 0)
        hbox_port.pack_start(btn_listen, False, False, 0)
        
        vbox.pack_start(hbox_port, False, False, 0)
        
        # Combo de protocolo
        self.combo_protocol = Gtk.ComboBoxText()
        self.combo_protocol.append_text("Contagem (bits)")
        self.combo_protocol.append_text("Inserção (bytes)")
        self.combo_protocol.set_active(0)
        vbox.pack_start(self.combo_protocol, False, False, 0)
        
        # Área de texto para logs
        self.buffer_display = Gtk.TextBuffer()
        textview = Gtk.TextView(buffer=self.buffer_display)
        textview.set_editable(False)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(textview)
        
        vbox.pack_start(scroll, True, True, 0)
        
        self.server_thread = None
        self.stop_server = threading.Event()
        
        self.set_default_size(450, 300)
        self.show_all()

    def on_listen_clicked(self, widget):
        """ Inicia o servidor TCP na porta escolhida. """
        port_str = self.entry_port.get_text().strip()
        if not port_str.isdigit():
            self.log_message("Porta inválida.")
            return
        
        port = int(port_str)
        if self.server_thread and self.server_thread.is_alive():
            self.log_message("Servidor já em execução.")
            return
        
        self.stop_server.clear()
        self.server_thread = threading.Thread(
            target=self.run_server,
            args=("0.0.0.0", port),
            daemon=True
        )
        self.server_thread.start()
        self.log_message(f"Servidor iniciado na porta {port}.")

    def run_server(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.bind((host, port))
            srv.listen(5)
            srv.settimeout(1.0)  # timeout para poder checar stop_server
            
            while not self.stop_server.is_set():
                try:
                    client_socket, addr = srv.accept()
                except socket.timeout:
                    continue
                
                self.log_message_threadsafe(f"Conexão de {addr}")
                
                # Receber todos os dados
                data = b""
                with client_socket:
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        data += chunk
                
                if data:
                    self.process_received_data(data, addr)

    def process_received_data(self, data: bytes, addr):
        """
        De acordo com o protocolo (contagem bits ou inserção bytes),
        exibe o quadro e desenquadra.
        """
        proto = self.combo_protocol.get_active_text()
        
        if proto == "Contagem (bits)":
            # Recebemos 'data' como ASCII que representa bits
            bits_str = ascii_to_bits(data)  # converte b'010101' -> '010101'
            self.log_message_threadsafe(f"Quadro bruto (bits, ASCII): {bits_str}")
            
            try:
                resultado = desenquadrar_contagem_caracteres(bits_str)
                self.log_message_threadsafe(f"Desenquadrado (bits): {resultado}")
            except Exception as e:
                self.log_message_threadsafe(f"Erro ao desenquadrar (bits): {e}")
        
        else:  # Inserção (bytes)
            # 'data' é o quadro real com flags e escapes
            # exibir em hexa para fins de debug
            self.log_message_threadsafe(f"Quadro bruto (hex): {data.hex()}")
            
            try:
                resultado = desenquadrar_insercao_bytes(data)
                self.log_message_threadsafe(f"Desenquadrado (ASCII): {resultado}")
            except Exception as e:
                self.log_message_threadsafe(f"Erro ao desenquadrar (bytes): {e}")

    def log_message_threadsafe(self, msg):
        GObject.idle_add(self.log_message, msg)

    def log_message(self, msg):
        end_iter = self.buffer_display.get_end_iter()
        self.buffer_display.insert(end_iter, msg + "\n")

    def close_server(self):
        self.stop_server.set()

    def destroy(self):
        self.close_server()
        super().destroy()


# ------------------------------------------------------------
# Janela do Transmissor
# ------------------------------------------------------------
class TransmitterWindow(Gtk.Window):
    """
    Transmissor:
    - Escolhe IP e porta do receptor
    - Escolhe protocolo (contagem bits ou inserção bytes)
    - Enquadra e envia
    """
    def __init__(self):
        super().__init__(title="Transmissor (Simulação)")
        self.set_border_width(10)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Linha para IP e Porta
        hbox_net = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        lbl_ip = Gtk.Label(label="IP:")
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
        lbl_msg = Gtk.Label(label="Mensagem/Bits:")
        self.entry_msg = Gtk.Entry()
        self.entry_msg.set_text("01010111")  # Exemplo para contagem (bits)
        
        vbox.pack_start(lbl_msg, False, False, 0)
        vbox.pack_start(self.entry_msg, False, False, 0)
        
        # Combo protocolo
        self.combo_protocol = Gtk.ComboBoxText()
        self.combo_protocol.append_text("Contagem (bits)")
        self.combo_protocol.append_text("Inserção (bytes)")
        self.combo_protocol.set_active(0)
        vbox.pack_start(self.combo_protocol, False, False, 0)
        
        # Botão Enviar
        btn_send = Gtk.Button(label="Enviar")
        btn_send.connect("clicked", self.on_send_clicked)
        vbox.pack_start(btn_send, False, False, 0)
        
        # Área de log
        self.buffer_output = Gtk.TextBuffer()
        textview = Gtk.TextView(buffer=self.buffer_output)
        textview.set_editable(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(textview)
        
        vbox.pack_start(scroll, True, True, 0)
        
        self.set_default_size(450, 300)
        self.show_all()
    
    def on_send_clicked(self, widget):
        """Enquadra o dado e envia via socket TCP."""
        ip = self.entry_ip.get_text().strip()
        port_str = self.entry_port.get_text().strip()
        mensagem = self.entry_msg.get_text()
        
        if not port_str.isdigit():
            self.log(f"Porta inválida: {port_str}")
            return
        
        port = int(port_str)
        proto = self.combo_protocol.get_active_text()
        
        try:
            if proto == "Contagem (bits)":
                # Usuário deve ter digitado bits (ex '01010111')
                quadro_bits = enquadrar_contagem_caracteres(mensagem)
                # Precisamos enviar esses bits como texto ASCII
                quadro_bytes = bits_to_ascii(quadro_bits)
                # Exibir no log
                self.log(f"Enquadrado (bits): {quadro_bits}")
            else:
                # Inserção (bytes)
                # Usuário digitou texto ASCII (ex 'ola meu ~ nome } e jonas')
                quadro_bytes = enquadrar_insercao_bytes(mensagem)
                # Exibir em hex
                self.log(f"Enquadrado (hex): {quadro_bytes.hex()}")
        except Exception as e:
            self.log(f"Erro ao enquadrar: {e}")
            return
        
        # Enviar via socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, port))
                s.sendall(quadro_bytes)
            self.log(f"Enviado para {ip}:{port}")
        except Exception as e:
            self.log(f"Erro ao enviar: {e}")
    
    def log(self, msg):
        end_iter = self.buffer_output.get_end_iter()
        self.buffer_output.insert(end_iter, msg + "\n")


# ------------------------------------------------------------
# (Opcional) Janela Principal para abrir TX/RX
# ------------------------------------------------------------
class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simulação de Enlace - Principal")
        self.set_border_width(10)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        lbl_info = Gtk.Label(label="Escolha o módulo:")
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
