# cliente.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import socket
import threading

from config import HOST, PORT
from src.comunicacao.transmissor import Transmissor

class ClienteNetwork:
    def __init__(self):
        self.client_socket = None
        self.setup_network()
        
    def setup_network(self):
        try:
            # Configurar socket do cliente
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Conectando ao servidor {HOST}:{PORT}...")
            self.client_socket.connect((HOST, PORT))
            print("Conectado ao servidor!")
            
            # Criar transmissor
            self.transmissor = Transmissor(self, self.client_socket)
            self.transmissor.window.show_all()
                
        except Exception as e:
            print(f"Erro na configuração do cliente: {e}")
            return None
    
    def stop(self):
        if self.client_socket:
            self.client_socket.close()
    
    def __del__(self):
        self.stop()

def main():
    cliente = ClienteNetwork()
    Gtk.main()

if __name__ == "__main__":
    main()