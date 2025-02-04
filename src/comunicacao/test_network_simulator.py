import logging
from src.fisica.digital import ModulacaoDigital
from src.enlace.enquadramento import (
    enquadrar_contagem_caracteres,
    enquadrar_insercao_bytes,
    desenquadrar_contagem_caracteres,
    desenquadrar_insercao_bytes,
)
from src.enlace.detecao_erro import calcular_paridade, verificar_paridade, calcular_crc, verificar_crc
from src.enlace.correcao_erro import gerar_hamming, corrigir_hamming, extrair_bits_hamming
from src.comunicacao.utils.ruido import inject_random_errors

# Funções auxiliares
def bytes_to_bits(data):
    """Convert bytes to bit list [1, 0, 1, ...]"""
    return [int(bit) for bit in ''.join(format(byte, '08b') for byte in data)]


def bits_to_string(bits):
    """Convert bit list to string"""
    bit_str = ''.join(map(str, bits))
    bytes_data = bytes(int(bit_str[i:i+8], 2) for i in range(0, len(bit_str), 8))
    return bytes_data.decode('utf-8')

def encode_message(message, modulacao, enquadramento, metodo_erro, polinomio_crc='1101', ruido = False):
    # 1. Enquadramento
    if enquadramento == 'Contagem':
        framed_message = enquadrar_contagem_caracteres(message)
    else:
        framed_message = enquadrar_insercao_bytes(message)
    
    # Certifique-se de que o resultado do enquadramento está em formato de bytes
    if isinstance(framed_message, str):  # Se for uma string, converta para bytes
        framed_message = framed_message.encode('utf-8')
    
    print(f"Framed message (bytes): {framed_message}")
    
    # 2. Converter mensagem enquadrada para bits (converter os bytes em bits)
    bits = ''.join(format(byte, '08b') for byte in framed_message)
    print(f"Bits: {bits}")

    # 3. metodo de erro
    if metodo_erro == 'Hamming (Correção)':
        bits_processados = gerar_hamming(bits)  # Usa Hamming (correção)
    elif metodo_erro == 'CRC (Detecção)':
        bits_processados = calcular_crc(bits, polinomio_crc)  # Detecção CRC
    elif metodo_erro == 'Paridade (Detecção)':
        bits_processados = calcular_paridade(bits)  # Detecção Paridade
    else:
        bits_processados = bits
    

    print(f"Bits processados: {bits_processados}")

    #3.1 aplicar ruido
    if ruido:
        bits_processados = inject_random_errors(bits_processados, error_prob=0.01)
        print(f"[ERRO] Bits após ruído: {bits_processados}")
    
    # 4. Modulação
    if modulacao == 'NRZ-Polar':
        modulated_message = ModulacaoDigital(list(map(int, bits_processados))).nrz_polar()
    elif modulacao == 'Manchester':
        modulated_message = ModulacaoDigital(list(map(int, bits_processados))).manchester()
    else:  # Bipolar
        modulated_message = ModulacaoDigital(list(map(int, bits_processados))).bipolar()
    
    
    print(f"Modulated message: {modulated_message}")
    return modulated_message

def decode_message(received_data, modulacao, enquadramento, metodo_erro, polinomio=None, logger=None):
    # Se nenhum logger for passado, criar um logger básico
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info(f"Received raw data: {received_data}")

    # 1. Demodulação
    if modulacao == 'NRZ-Polar':
        demodulated_bits = ModulacaoDigital.demodular_nrz_polar(received_data)
    elif modulacao == 'Manchester':
        demodulated_bits = ModulacaoDigital.demodular_manchester(received_data)
    else:  # Bipolar
        demodulated_bits = ModulacaoDigital.demodular_bipolar(received_data)

    demodulated_bits_str = ''.join(map(str, demodulated_bits))
    logger.info(f"Demodulated bits: {demodulated_bits_str}")

    # 2. Verificar detecção/correção de erro
    if metodo_erro == 'CRC (Detecção)':
        if not verificar_crc(demodulated_bits_str, polinomio):
            logger.error("CRC inválido! Mensagem descartada.")
            return None  # Não processa a mensagem
        original_bits = demodulated_bits_str[:-(len(polinomio) - 1)]
    
    elif metodo_erro == 'Paridade (Detecção)':
        if not verificar_paridade(demodulated_bits_str):
            logger.error("Paridade inválida! Mensagem descartada.")
            return None  # Não processa a mensagem
        original_bits = demodulated_bits_str[:-1]
    
    elif metodo_erro == 'Hamming (Correção)':
        bits_corrigidos = corrigir_hamming(demodulated_bits_str)
        original_bits = extrair_bits_hamming(bits_corrigidos)
        logger.info(f"Bits após correção: {original_bits}")
    else:
        original_bits = demodulated_bits_str

    logger.info(f"Original bits (without error detection): {original_bits}")

    # 3. Converter bits para bytes
    original_bytes = bytes(int(original_bits[i:i+8], 2) for i in range(0, len(original_bits), 8))
    logger.info(f"Original bytes: {original_bytes}")

    # 4. Desenquadramento
    if enquadramento == 'Contagem':
        original_message = desenquadrar_contagem_caracteres(original_bytes)
    else:
        original_message = desenquadrar_insercao_bytes(original_bytes)
        

    logger.info(f"Decoded message: {original_message.decode('utf-8')}")
    return original_message.decode('utf-8')

# Testes
if __name__ == "__main__":
    # Configurações para teste
    test_message = "10000001"
    test_modulacao = "NRZ-Polar"  # Testar com "Manchester" ou "Bipolar"
    test_enquadramento = "Contagem"  # Testar com "contagem de caracteres ou insercao de bytes"
    deteccao_erro = "CRC"  # Testar com "Paridade" ou "CRC"
    polinomio_crc = "1101"  # Usado para CRC

    print("=== TESTING ENCODE & DECODE ===")

    # Codificar a mensagem
    encoded = encode_message(test_message, test_modulacao, test_enquadramento, deteccao_erro, polinomio_crc)

    # Decodificar a mensagem
    decoded = decode_message(encoded, test_modulacao, test_enquadramento, deteccao_erro, polinomio_crc)
    print(f"\nFinal Decoded Message: {decoded}")
