import multiprocessing
import subprocess
import sys
import time

def start_servidor():
    """Executa o servidor."""
    try:
        print("[Servidor] Iniciando...")
        subprocess.run([sys.executable, "servidor.py"])
    except Exception as e:
        print(f"[Servidor] Erro: {e}")

def start_cliente():
    """Executa o cliente."""
    try:
        print("[Cliente] Iniciando...")
        subprocess.run([sys.executable, "cliente.py"])
    except Exception as e:
        print(f"[Cliente] Erro: {e}")

def main():
    # Criar processo do servidor
    servidor_process = multiprocessing.Process(target=start_servidor, daemon=True)
    servidor_process.start()
    print("[Main] Servidor iniciado. Aguardando inicialização...")

    # Aguardar o servidor estar pronto antes de iniciar o cliente
    time.sleep(1)  # Ajuste conforme o tempo necessário para o servidor estar ativo

    # Criar processo do cliente
    cliente_process = multiprocessing.Process(target=start_cliente, daemon=True)
    cliente_process.start()
    print("[Main] Cliente iniciado.")

    print("[Main] Servidor e cliente estão em execução. Pressione Ctrl+C para encerrar.")

    try:
        # Manter o script principal ativo até que os processos sejam encerrados
        while servidor_process.is_alive() and cliente_process.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[Main] Encerrando processos...")
        servidor_process.terminate()
        cliente_process.terminate()

    # Garantir que ambos os processos sejam finalizados
    servidor_process.join()
    cliente_process.join()
    print("[Main] Processos encerrados com sucesso.")

if __name__ == "__main__":
    main()