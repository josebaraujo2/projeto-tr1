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
    return paridade == int(bits_com_paridade[-1])

def calcular_crc(bits, polinomio):
    """
    Transmissor
    Protocolo de Detecção de Erros: CRC
    Calcula o CRC para a sequência de bits e adiciona ao final.
    """
    bits_dividendo = bits + '0' * (len(polinomio) - 1)
    bits_divisor = polinomio

    bits_dividendo = list(bits_dividendo)
    for i in range(len(bits)):
        if bits_dividendo[i] == '1':
            for j in range(len(bits_divisor)):
                bits_dividendo[i + j] = str(int(bits_dividendo[i + j]) ^ int(bits_divisor[j]))
    crc = ''.join(bits_dividendo[-(len(polinomio) - 1):])
    return bits + crc

def verificar_crc(bits_com_crc, polinomio):
    """
    Receptor
    Verifica a integridade da sequência de bits usando CRC.
    """
    bits_dividendo = list(bits_com_crc)
    bits_divisor = polinomio

    for i in range(len(bits_com_crc) - len(polinomio) + 1):
        if bits_dividendo[i] == '1':
            for j in range(len(bits_divisor)):
                bits_dividendo[i + j] = str(int(bits_dividendo[i + j]) ^ int(bits_divisor[j]))

    resto = ''.join(bits_dividendo[-(len(polinomio) - 1):])
    return resto == '0' * (len(polinomio) - 1)
