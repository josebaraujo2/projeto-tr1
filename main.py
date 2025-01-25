import gi
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.comunicacao.gerenciador_socket import create_socket_server, create_socket_client, inject_errors
from src.comunicacao.transmissor import Transmissor
from src.comunicacao.receptor import Receptor
import time

class NetworkSimulator:
    def __init__(self):
        self.server_socket = create_socket_server()
        self.client_socket = None
        self.receptor = None
        self.transmissor = None

    def start_server(self):
        # Inicia a thread do servidor que aguarda a conexão
        print("Aguardando conexão...")
        self.server_socket.listen(1)  # Escuta por uma conexão

        conn, addr = self.server_socket.accept()
        print(f"Conexão estabelecida com {addr}")

        # Agora que a conexão foi estabelecida, cria o socket do cliente
        self.client_socket = create_socket_client()

        # Inicializa o transmissor e receptor com os sockets corretos
        self.receptor = Receptor(self, conn)
        self.transmissor = Transmissor(self, self.client_socket)

        # Exibe as janelas depois que o transmissor e o receptor são inicializados
        self.transmissor.window.show_all()
        self.receptor.window.show_all()

        # Cria threads para o transmissor e o receptor
        receptor_thread = threading.Thread(target=self.receptor.receive_message)
        transmissor_thread = threading.Thread(target=self.transmissor.transmit_message, args=("Mensagem de teste",))
        
        receptor_thread.start()
        transmissor_thread.start()

        Gtk.main()

    def start_client(self):
        # Inicializa o cliente e envia uma mensagem
        client_socket = create_socket_client()
        print("Cliente conectado.")
        time.sleep(1)  # Espera um pouco para garantir que o servidor esteja pronto
        client_socket.send(b"Mensagem de teste")
        client_socket.close()

    def start(self):
        # Cria as threads para o servidor e o cliente
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

        # Inicializa o cliente após uma pequena pausa
        time.sleep(1)
        client_thread = threading.Thread(target=self.start_client)
        client_thread.start()

def main():
    simulator = NetworkSimulator()
    simulator.start()  # Inicia a simulação

if __name__ == "__main__":
    main()
