import random

def inject_random_errors(bitstring, error_prob=0.01):
    """Introduz erros em uma string de bits (ex: '1010') com probabilidade 0.01% por bit"""
    bits = list(bitstring)
    for i in range(len(bits)):
        if random.random() < error_prob:
            bits[i] = '1' if bits[i] == '0' else '0'
    return ''.join(bits)