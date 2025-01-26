import multiprocessing
import subprocess
import sys

def start_servidor():
    """Executa o servidor."""
    subprocess.run([sys.executable, "servidor.py"])

def start_cliente():
    """Executa o cliente."""
    subprocess.run([sys.executable, "cliente.py"])

def main():
    # Criar processos separados para servidor e cliente
    servidor_process = multiprocessing.Process(target=start_servidor, daemon=True)
    cliente_process = multiprocessing.Process(target=start_cliente, daemon=True)

    # Iniciar processos
    servidor_process.start()
    cliente_process.start()

    print("Servidor e cliente iniciados. Pressione Ctrl+C para encerrar.")

    try:
        # Manter o script principal ativo
        servidor_process.join()
        cliente_process.join()
    except KeyboardInterrupt:
        print("\nEncerrando...")
        servidor_process.terminate()
        cliente_process.terminate()

if __name__ == "__main__":
    main()
