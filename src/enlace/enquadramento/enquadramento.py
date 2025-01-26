def enquadrar_contagem_caracteres(dados, tamanho_quadro=8):
    """
    Enquadramento por Contagem de Caracteres em nível de bits.
    Formato: [Número de Bits (8 bits)][Dados (até 'tamanho_quadro' bits)]
    """
    quadros = ''
    for i in range(0, len(dados), tamanho_quadro):
        chunk = dados[i:i+tamanho_quadro]
        tamanho = format(len(chunk), '08b')  # 8 bits para o tamanho
        quadros += tamanho + chunk
    return quadros

def desenquadrar_contagem_caracteres(quadro):
    """
    Desenquadra sequência de bits com formato: [Número de Bits (8 bits)][Dados].
    """
    dados = ''
    i = 0
    while i < len(quadro):
        num_bits = int(quadro[i:i+8], 2)  # converte 8 bits em inteiro
        i += 8
        dados += quadro[i:i+num_bits]
        i += num_bits
    return dados

def enquadrar_insercao_bytes(dados):
    """
    Enquadramento com Inserção de Bytes.
    Formato: [Flag=0x7E][Dados Escapados][Flag=0x7E]
    """
    flag = b'\x7E'
    escape = b'\x7D'
    dados_escapados = b''
    for byte in dados.encode('ascii'):
        if byte == flag[0] or byte == escape[0]:
            dados_escapados += escape + bytes([byte ^ 0x20])
        else:
            dados_escapados += bytes([byte])
    quadro = flag + dados_escapados + flag
    return quadro

def desenquadrar_insercao_bytes(quadro):
    """
    Desenquadramento com Inserção de Bytes.
    Remove as flags (0x7E) e processa escapes (0x7D).
    Retorna uma string ASCII.
    """
    flag = b'\x7E'
    escape = b'\x7D'
    if not (quadro.startswith(flag) and quadro.endswith(flag)):
        raise ValueError("Quadro inválido: flags de início/fim ausentes.")
    dados_escapados = quadro[1:-1]  # remove as flags
    dados = b''
    skip = False
    for i in range(len(dados_escapados)):
        byte = dados_escapados[i]
        if skip:
            dados += bytes([byte ^ 0x20])
            skip = False
        elif byte == escape[0]:
            skip = True
        else:
            dados += bytes([byte])
    return dados.decode('ascii')
