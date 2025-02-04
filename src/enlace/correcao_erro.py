import numpy as np
def gerar_hamming(bits):
    """
    Transmissor
    Protocolo de Correção de Erros: Código de Hamming
    Gera uma sequência com bits de paridade para correção de erros.
    """
    n = len(bits)
    r = 0
    while (2 ** r) < (n + r + 1):
        r += 1

    hamming = ['0'] * (n + r)
    j = 0
    for i in range(1, len(hamming) + 1):
        if i & (i - 1) == 0:  # Potência de 2
            continue
        hamming[i - 1] = bits[j]
        j += 1

    for i in range(r):
        pos = 2 ** i
        valor_paridade = 0
        for j in range(1, len(hamming) + 1):
            if j & pos == pos:
                valor_paridade ^= int(hamming[j - 1])
        hamming[pos - 1] = str(valor_paridade)

    return ''.join(hamming)

def corrigir_hamming(bits_hamming):
    """
    Receptor
    Verifica e corrige erros em uma sequência codificada com Hamming.
    """
    n = len(bits_hamming)
    r = 0
    while (2 ** r) < n:
        r += 1

    erro_pos = 0
    for i in range(r):
        pos = 2 ** i
        valor_paridade = 0
        for j in range(1, len(bits_hamming) + 1):
            if j & pos == pos:
                valor_paridade ^= int(bits_hamming[j - 1])
        if valor_paridade != 0:
            erro_pos += pos

    if erro_pos:
        bits_hamming = list(bits_hamming)
        bits_hamming[erro_pos - 1] = '1' if bits_hamming[erro_pos - 1] == '0' else '0'

    return ''.join(bits_hamming)

def extrair_bits_hamming(bits_corrigidos):
    n = len(bits_corrigidos)
    bits_originais = []
    pos_paridade = [2**i - 1 for i in range(int(np.log2(n)) + 1)]  # Posições de paridade
    for i in range(n):
        if i not in pos_paridade:
            bits_originais.append(bits_corrigidos[i])
    return ''.join(bits_originais)