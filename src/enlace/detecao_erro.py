def calcular_paridade(bits):
    """
    Transmissor
    Protocolo de Detecção de Erros: Bit de Paridade Par
    Adiciona um bit de paridade ao final da sequência de bits.
    """
    paridade = bits.count('1') % 2
    bits_com_paridade = bits + ('0' if paridade == 0 else '1')
    return bits_com_paridade

def verificar_paridade(bits_com_paridade):
    """
    Receptor
    Verifica a integridade da sequência usando o bit de paridade.
    """
    paridade = bits_com_paridade[:-1].count('1') % 2
    return paridade == int(bits_com_paridade[:-1])

def calcular_crc(bits, polinomio):
    len_polinomio = len(polinomio)
    dividendo = list(bits) + ['0'] * (len_polinomio - 1)
    polinomio = list(polinomio)

    for i in range(len(dividendo) - len_polinomio + 1):
        if dividendo[i] == '1':
            for j in range(len_polinomio):
                dividendo[i + j] = '1' if dividendo[i + j] != polinomio[j] else '0'

    crc = ''.join(dividendo[-(len_polinomio - 1):])
    return bits + crc

def verificar_crc(bits_com_crc, polinomio):
    len_polinomio = len(polinomio)
    dividendo = list(bits_com_crc)
    polinomio = list(polinomio)

    for i in range(len(dividendo) - len_polinomio + 1):
        if dividendo[i] == '1':
            for j in range(len_polinomio):
                dividendo[i + j] = '1' if dividendo[i + j] != polinomio[j] else '0'

    resto = ''.join(dividendo[-(len_polinomio - 1):])
    return all(bit == '0' for bit in resto)