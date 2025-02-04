import random

def inject_random_errors(bitstring, error_prob=0.05):
    bits = list(bitstring)
    error_count = 0
    for i in range(len(bits)):
        if random.random() < error_prob:
            bits[i] = '1' if bits[i] == '0' else '0'
            error_count += 1
    if error_count:
        print(f"[DEBUG] Foram injetados {error_count} erros em {len(bits)} bits.")
    return ''.join(bits)