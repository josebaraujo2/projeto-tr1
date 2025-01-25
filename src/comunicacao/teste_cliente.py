import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))  # O mesmo endereço e porta
    client_socket.send(b"Mensagem de teste")
    client_socket.close()

if __name__ == "__main__":
    start_client()