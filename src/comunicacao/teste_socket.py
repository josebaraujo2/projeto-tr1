import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))  # Certifique-se de que a porta está disponível
    server_socket.listen(1)
    print("Servidor aguardando conexão...")
    conn, addr = server_socket.accept()
    print(f"Conexão estabelecida com {addr}")
    data = conn.recv(1024)
    print(f"Recebido: {data}")
    conn.close()

if __name__ == "__main__":
    start_server()