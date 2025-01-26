# Imports necessários
from src.fisica.digital import ModulacaoDigital
from src.enlace.enquadramento import (
    enquadrar_contagem_caracteres,
    enquadrar_insercao_bytes,
    desenquadrar_contagem_caracteres,
    desenquadrar_insercao_bytes,
)
from src.enlace.detecao_erro import calcular_paridade, verificar_paridade, calcular_crc, verificar_crc


# Funções auxiliares
def bytes_to_bits(data):
    """Convert bytes to bit list [1, 0, 1, ...]"""
    return [int(bit) for bit in ''.join(format(byte, '08b') for byte in data)]


def bits_to_string(bits):
    """Convert bit list to string"""
    bit_str = ''.join(map(str, bits))
    bytes_data = bytes(int(bit_str[i:i+8], 2) for i in range(0, len(bit_str), 8))
    return bytes_data.decode('utf-8')


# Função para codificar mensagem
def encode_message(message, modulacao, enquadramento, deteccao_erro, polinomio_crc):
    # 1. Enquadramento
    if enquadramento == 'Contagem':
        framed_message = enquadrar_contagem_caracteres(message)
    else:
        framed_message = enquadrar_insercao_bytes(message)
    
    # Certifique-se de que o resultado do enquadramento está em formato de bytes
    if isinstance(framed_message, str):  # Se for uma string, converta para bytes
        framed_message = framed_message.encode('utf-8')
    
    print(f"Framed message (bytes): {framed_message}")
    
    # 2. Convert framed message to bits
    bits = ''.join(format(byte, '08b') for byte in framed_message)
    print(f"Bits: {bits}")
    
    # 3. Adicionar CRC, se necessário
    if deteccao_erro == 'CRC' and polinomio_crc:
        bits_with_crc = calcular_crc(bits, polinomio_crc)
        print(f"Bits with CRC: {bits_with_crc}")
    else:
        bits_with_crc = bits  # Se não for CRC, use os bits sem CRC
    
    # 4. Modulação
    if modulacao == 'NRZ-Polar':
        modulated_message = ModulacaoDigital(list(map(int, bits_with_crc))).nrz_polar()
    elif modulacao == 'Manchester':
        modulated_message = ModulacaoDigital(list(map(int, bits_with_crc))).manchester()
    else:  # Bipolar
        modulated_message = ModulacaoDigital(list(map(int, bits_with_crc))).bipolar()
    
    print(f"Modulated message: {modulated_message}")
    return modulated_message


# Função para decodificar mensagem
def decode_message(received_data, modulacao, enquadramento, deteccao_erro, polinomio=None):
    print("\n=== Decoding Message ===")
    print(f"Received raw data: {received_data}")

    # 1. Demodulação
    if modulacao == 'NRZ-Polar':
        demodulated_bits = ModulacaoDigital.demodular_nrz_polar(received_data)
    elif modulacao == 'Manchester':
        demodulated_bits = ModulacaoDigital.demodular_manchester(received_data)
    else:  # Bipolar
        demodulated_bits = ModulacaoDigital.demodular_bipolar(received_data)

    demodulated_bits_str = ''.join(map(str, demodulated_bits))
    print(f"Demodulated bits: {demodulated_bits_str}")

    # 2. Verificar detecção de erro
    if deteccao_erro == 'Paridade':
        if not verificar_paridade(demodulated_bits_str):
            print("Parity check failed")
            return None
        original_bits = demodulated_bits_str[:-1]
    elif deteccao_erro == 'CRC' and polinomio:
        if not verificar_crc(demodulated_bits_str, polinomio):
            print("CRC check failed")
            return None
        original_bits = demodulated_bits_str[:-(len(polinomio) - 1)]
    else:
        raise ValueError("Método de detecção de erro inválido ou polinômio não fornecido para CRC.")

    print(f"Original bits (without error detection): {original_bits}")

    # 3. Converter bits para bytes
    original_bytes = bytes(int(original_bits[i:i+8], 2) for i in range(0, len(original_bits), 8))
    print(f"Original bytes: {original_bytes}")

    # 4. Desenquadramento
    if enquadramento == 'Contagem':
        original_message = desenquadrar_contagem_caracteres(original_bytes)
    else:
        original_message = desenquadrar_insercao_bytes(original_bytes)

    print(f"Decoded message: {original_message.decode('utf-8')}")
    return original_message.decode('utf-8')


# Testes
if __name__ == "__main__":
    # Configurações para teste
    test_message = "ola, meu nome e jose!"
    test_modulacao = "NRZ-Polar"  # Testar com "Manchester" ou "Bipolar"
    test_enquadramento = "Contagem"  # Testar com "Inserção Bytes"
    deteccao_erro = "CRC"  # Testar com "Paridade" ou "CRC"
    polinomio_crc = "1101"  # Usado para CRC

    print("=== TESTING ENCODE & DECODE ===")

    # Codificar a mensagem
    encoded = encode_message(test_message, test_modulacao, test_enquadramento, deteccao_erro, polinomio_crc)

    # Decodificar a mensagem
    decoded = decode_message(encoded, test_modulacao, test_enquadramento, deteccao_erro, polinomio_crc)
    print(f"\nFinal Decoded Message: {decoded}")
