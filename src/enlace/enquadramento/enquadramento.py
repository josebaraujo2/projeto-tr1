import struct

# Definições para Byte Stuffing
FLAG = 0x7E  # 01111110 em binário
ESC  = 0x7D  # 01111101 em binário
ESC_XOR = 0x20  # Usado para "escapar"

def enquadra_contagem(msg: str) -> bytes:
    """
    Protocolo de contagem de caracteres (em bytes).
    - Insere 2 bytes (unsigned short) no início, indicando o tamanho dos dados.
    - Em seguida, insere a carga útil (os bytes da msg).
    """
    dados = msg.encode('utf-8')  # converte string para bytes (UTF-8, por exemplo)
    tamanho = len(dados)
    # 2 bytes (big-endian) para representar o tamanho
    header = struct.pack('>H', tamanho)
    quadro = header + dados
    return quadro

def desenquadra_contagem(quadro: bytes) -> str:
    """
    Desenquadra (contagem de caracteres).
    - Lê 2 bytes iniciais para saber quantos bytes de dados devem ser lidos.
    - Retorna a string original (UTF-8).
    """
    if len(quadro) < 2:
        raise ValueError("Quadro menor que 2 bytes, não é possível ler o tamanho.")
    
    tamanho = struct.unpack('>H', quadro[:2])[0]  # Lê o tamanho
    if len(quadro) < 2 + tamanho:
        raise ValueError("O quadro recebido é menor do que o tamanho indicado.")

    dados = quadro[2:2 + tamanho]
    return dados.decode('utf-8')

def enquadra_insercao(msg: str) -> bytes:
    """
    Protocolo de inserção de bytes (Byte Stuffing).
    - Usa FLAG (0x7E) como delimitador de quadro e ESC (0x7D) para escape.
    """
    dados = msg.encode('utf-8')
    quadro = bytearray()
    
    # FLAG inicial
    quadro.append(FLAG)
    
    for b in dados:
        if b == FLAG or b == ESC:
            quadro.append(ESC)
            quadro.append(b ^ ESC_XOR)
        else:
            quadro.append(b)
    
    # FLAG final
    quadro.append(FLAG)
    return bytes(quadro)

def desenquadra_insercao(quadro: bytes) -> str:
    """
    Desenquadra (byte stuffing).
    - Considera somente UM par FLAG ... FLAG.
    - Retorna a string (UTF-8).
    """
    # Procurar FLAG inicial
    i = 0
    while i < len(quadro) and quadro[i] != FLAG:
        i += 1
    
    if i >= len(quadro):
        raise ValueError("Nenhuma FLAG inicial encontrada no quadro.")
    
    i += 1  # pular a FLAG inicial
    dados_reais = bytearray()
    
    while i < len(quadro) and quadro[i] != FLAG:
        if quadro[i] == ESC:
            # Próximo byte deve ser XOR com ESC_XOR
            i += 1
            if i < len(quadro):
                dados_reais.append(quadro[i] ^ ESC_XOR)
            else:
                raise ValueError("ESC encontrado no final do quadro sem próximo byte.")
        else:
            dados_reais.append(quadro[i])
        i += 1
    
    # i agora está na FLAG final (ou no fim)
    return dados_reais.decode('utf-8')
