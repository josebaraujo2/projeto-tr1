import socket
import random

def create_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))  # Ou qualquer outra porta desejada
    server_socket.listen(1)
    print("Servidor ouvindo na porta 12345...")
    return server_socket

def create_socket_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))  # Conecta-se ao servidor
    print("Cliente conectado ao servidor!")
    return client_socket


import random

def inject_errors(signal, error_rate=0.01):
    """
    Randomly introduces errors into the given signal.

    Args:
        signal (list): The signal as a list of bits or modulated values.
        error_rate (float, optional): The probability of an error occurring. Defaults to 0.01 (1%).

    Returns:
        list: The signal with errors injected.
    """
    corrupted_signal = signal[:]
    for i in range(len(corrupted_signal)):
        if random.random() < error_rate:
            # Para sinais binários, invertemos o valor (0 <-> 1)
            if isinstance(corrupted_signal[i], int):
                corrupted_signal[i] = 1 - corrupted_signal[i]
            # Para sinais modulares, podemos adicionar um pequeno erro ao valor
            else:
                corrupted_signal[i] += random.uniform(-0.1, 0.1)  # Adicionando erro aleatório
    return corrupted_signal