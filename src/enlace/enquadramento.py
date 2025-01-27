def enquadrar_contagem_caracteres(dados, tamanho_quadro=8):
    """
    Enquadramento por Contagem de Caracteres em nível de bits.
    Formato: [Número de Bits][Dados]
    """
    quadros = b''  # Use 'bytes' ao invés de 'string'
    for i in range(0, len(dados), tamanho_quadro):
        chunk = dados[i:i+tamanho_quadro]
        # Adiciona cabeçalho com tamanho e dados do chunk
        tamanho = format(len(chunk), '08b')  # Tamanho como 8 bits
        quadros += bytes(tamanho, 'utf-8') + chunk.encode('utf-8')  # Convertendo chunk para bytes
    return quadros

def desenquadrar_contagem_caracteres(quadro):
    """
    Desenquadra sequência de bits com tamanho fixo de quadros.
    Formato: [Número de Bits][Dados]
    """
    dados = b''  # Use 'bytes' ao invés de 'string'
    i = 0
    while i < len(quadro):
        # O primeiro byte (8 bits) é o tamanho
        num_bits = int(quadro[i:i+8], 2)  # Converte os primeiros 8 bits para inteiro
        i += 8  # Avança 8 bits
        dados += quadro[i:i+num_bits]  # Adiciona os bits conforme o número indicado
        i += num_bits  # Avança os bits lidos
    return dados

def enquadrar_insercao_bytes(dados):
    """
    Enquadramento com Inserção de Bytes.
    Formato: [Flag][Dados Escapados][Flag]
    """
    flag = b'\x7E'
    escape = b'\x7D'

    # Escapa os bytes especiais nos dados
    dados_escapados = b''
    for byte in dados.encode('ascii'):
        if byte == flag[0] or byte == escape[0]:
            # Adiciona o escape byte e faz XOR com 0x20
            dados_escapados += escape + bytes([byte ^ 0x20])
        else:
            dados_escapados += bytes([byte])
    
    # Adiciona a flag no início e no final
    quadro = flag + dados_escapados + flag
    return quadro


def desenquadrar_insercao_bytes(quadro):
    # Flag e escape bytes
    flag = b'\x7E'
    escape = b'\x7D'
    
    # Verifica se o quadro começa e termina com as flags corretas
    if not (quadro.startswith(flag) and quadro.endswith(flag)):
        raise ValueError("Quadro inválido: flags de início/fim ausentes.")
    
    # Remove as flags de início e fim
    dados_escapados = quadro[1:-1]  # remove as flags
    dados = b''
    skip = False

    for i in range(len(dados_escapados)):
        byte = dados_escapados[i]
        if skip:
            dados += bytes([byte ^ 0x20])  # Remove o escape aplicando XOR novamente
            skip = False
        elif byte == escape[0]:
            skip = True  # Quando encontrar o byte de escape, marcar para aplicar o XOR no próximo byte
        else:
            dados += bytes([byte])

    # Agora, temos os dados "limpos" sem as flags e sem escapes
    return dados


# Exemplo de uso
dados = "ola meu ~ nome } e jonas"
quadro_contagem = enquadrar_contagem_caracteres(dados)
quadro_insercao = enquadrar_insercao_bytes(dados)

'''
print("Contagem de Caracteres:")
print(f"Quadro: {quadro_contagem}")
print(f"Dados Originais: {desenquadrar_contagem_caracteres(quadro_contagem)}\n")

print("Inserção de Bytes:")
print(f"Quadro: {quadro_insercao}")
print(f"Dados Originais: {desenquadrar_insercao_bytes(quadro_insercao)}")
'''