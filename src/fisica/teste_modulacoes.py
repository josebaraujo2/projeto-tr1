import numpy as np
import matplotlib.pyplot as plt
from digital import ModulacaoDigital
from portadora import ModulacaoPortadora

def generate_random_bits(length=100, seed=42):
    """Generate random bit sequence"""
    np.random.seed(seed)
    return np.random.randint(2, size=length).tolist()

def detailed_comparison(original, decoded, modulation_type):
    """Detailed comparison of original and decoded bits"""
    errors = [i for i in range(len(original)) if original[i] != decoded[i]]
    
    plt.figure(figsize=(15, 5))
    plt.subplot(2, 1, 1)
    plt.title(f"{modulation_type} - Original vs Decoded Bits")
    plt.plot(original, label='Original', marker='o')
    plt.plot(decoded, label='Decoded', marker='x')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    error_positions = np.zeros(len(original))
    error_positions[errors] = 1
    plt.title("Error Positions")
    plt.plot(error_positions, 'r')
    
    plt.tight_layout()
    plt.show()
    
    print(f"{modulation_type} Debugging:")
    print(f"Total Bits: {len(original)}")
    print(f"Error Positions: {errors}")
    print(f"Error Rate: {len(errors)/len(original):.2%}")
    
def test_digital_modulation():
    """Test digital modulation and demodulation techniques with debugging"""
    bits = generate_random_bits()
    
    digital_mod = ModulacaoDigital(bits)
    
    # NRZ-Polar
    nrz_signal = digital_mod.nrz_polar()
    nrz_demod = ModulacaoDigital.demodular_nrz_polar(nrz_signal)
    detailed_comparison(bits, nrz_demod, "NRZ-Polar")
    
    # Manchester
    manchester_signal = digital_mod.manchester()
    manchester_demod = ModulacaoDigital.demodular_manchester(manchester_signal)
    detailed_comparison(bits, manchester_demod, "Manchester")
    
    # Bipolar
    bipolar_signal = digital_mod.bipolar()
    bipolar_demod = ModulacaoDigital.demodular_bipolar(bipolar_signal)
    detailed_comparison(bits, bipolar_demod, "Bipolar")

def test_carrier_modulation():
    """Test carrier modulation and demodulation techniques with debugging"""
    bits = generate_random_bits()
    
    carrier_mod = ModulacaoPortadora(bits)
    
    # ASK
    ask_tempo, ask_sinal = carrier_mod.ask()
    ask_demod = ModulacaoPortadora.demodular_ask(ask_tempo, ask_sinal)
    detailed_comparison(bits, ask_demod, "ASK")
    
    # FSK
    fsk_tempo, fsk_sinal = carrier_mod.fsk()
    fsk_demod = ModulacaoPortadora.demodular_fsk(fsk_tempo, fsk_sinal)
    detailed_comparison(bits, fsk_demod, "FSK")
    
    # 8-QAM
    qam_tempo, qam_sinal = carrier_mod.qam8()
    qam_demod = ModulacaoPortadora.demodular_qam8_refinado(qam_tempo, qam_sinal)
    detailed_comparison(bits[:len(qam_demod)], qam_demod, "8-QAM")

def main():
    test_carrier_modulation()

if __name__ == "__main__":
    main()