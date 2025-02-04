import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import socket
import threading
import pickle
import struct
from queue import Queue

from config import HOST, PORT
from src.comunicacao.receptor import Receptor

class ServidorNetwork:
    def __init__(self):
        self.server_socket = None
        self.running = True
        self.message_queue = Queue()
        self.setup_network()
        
    def setup_network(self):
        try:
            # Configurar socket do servidor
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(1)
            
            # Iniciar thread para aceitar conexões
            self.accept_thread = threading.Thread(target=self.accept_connection, daemon=True)
            self.accept_thread.start()
            
        except Exception as e:
            print(f"Erro na configuração do servidor: {e}")
            self.running = False
            return None

    def recvall(self, sock, n):
        data = bytearray()
        while len(data) < n and self.running:
            try:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except socket.timeout:
                continue
            except socket.error as e:
                if not isinstance(e, socket.timeout):
                    print(f"Erro ao receber dados: {e}")
                return None
        return data if self.running else None
    
    def accept_connection(self):
        try:
            print(f"Servidor iniciado em {HOST}:{PORT}")
            print("Aguardando conexão...")
            while self.running:
                self.server_socket.settimeout(1.0)
                try:
                    connection, addr = self.server_socket.accept()
                    print(f"Conexão estabelecida com {addr}")
                    
                    # Usar GLib.idle_add para garantir execução na thread principal
                    GLib.idle_add(self.setup_receptor, connection)
                    
                except socket.timeout:
                    if not self.running:
                        break
                    continue
                    
        except Exception as e:
            print(f"Erro na conexão: {e}")
    
    def setup_receptor(self, connection):
        """Configura o receptor na thread principal"""
        self.receptor = Receptor(self, connection)
        self.receptor.window.show_all()

        # Iniciar thread de recebimento
        self.receive_thread = threading.Thread(
            target=self.receive_loop, 
            args=(connection,), 
            daemon=True
        )
        self.receive_thread.start()

    def receive_loop(self, connection):
        connection.settimeout(1.0)
        
        while self.running:
            try:
                # Receber o tamanho do header
                header_size_data = self.recvall(connection, 4)
                if not header_size_data:
                    continue
                    
                header_size = struct.unpack('>I', header_size_data)[0]
                header_data = self.recvall(connection, header_size)
                if not header_data:
                    continue
                    
                header = pickle.loads(header_data)
                
                # Receber o tamanho dos dados
                data_size_data = self.recvall(connection, 4)
                if not data_size_data:
                    continue
                    
                data_size = struct.unpack('>I', data_size_data)[0]
                data = self.recvall(connection, data_size)
                if not data:
                    continue
                
                modulated_data = pickle.loads(data)
                
                # Adicionar mensagem à fila
                self.message_queue.put((modulated_data, header))
                
                # Processar a mensagem na GUI
                GLib.idle_add(self.process_message)
                
            except socket.timeout:
                continue
            except Exception as e:
                if not isinstance(e, socket.timeout):
                    print(f"Erro no receive_loop: {e}")
                if not self.running:
                    break
        
        connection.close()

    def process_message(self):
        if not self.message_queue.empty():
            modulated_data, header = self.message_queue.get()
            self.receptor.receive_message(
                modulated_data,
                header['modulacao'],
                header['enquadramento'],
                header['metodo_erro']
            )
        return False
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def __del__(self):
        self.stop()

def main():
    servidor = ServidorNetwork()
    Gtk.main()

if __name__ == "__main__":
    main()