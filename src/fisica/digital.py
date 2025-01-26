import numpy as np
import matplotlib.pyplot as plt

class ModulacaoDigital:
    def __init__(self, bits):
        self.bits = bits
        self.sampling_rate = 100  
        
    def _generate_time_base(self):
        return np.linspace(0, len(self.bits), len(self.bits) * self.sampling_rate)
    
    def nrz_polar(self):
        signal = []
        for bit in self.bits:
            level = 1 if bit == 1 else -1
            signal.extend([level] * self.sampling_rate)
        return np.array(signal)
    
    def manchester(self):
        signal = []
        for bit in self.bits:
            if bit == 1:
                signal.extend([1] * (self.sampling_rate//2))
                signal.extend([-1] * (self.sampling_rate//2))
            else:
                signal.extend([-1] * (self.sampling_rate//2))
                signal.extend([1] * (self.sampling_rate//2))
        return np.array(signal)
    
    def bipolar(self):
        signal = []
        last_polarity = 1
        
        for bit in self.bits:
            if bit == 0:
                signal.extend([0] * self.sampling_rate)
            else:
                signal.extend([last_polarity] * self.sampling_rate)
                last_polarity = -last_polarity
        
        return np.array(signal)

    def get_time_base(self):
        return self._generate_time_base()

    @staticmethod
    def demodular_nrz_polar(sinal_modulado):
        """Demodulação NRZ-Polar"""
        bits = [1 if np.mean(sinal_modulado[i:i+100]) > 0 else 0 
                for i in range(0, len(sinal_modulado), 100)]
        return bits

    @staticmethod
    def demodular_manchester(sinal_modulado):
        """Demodulação Manchester"""
        bits = []
        for i in range(0, len(sinal_modulado), 100):
            primeira_metade = np.mean(sinal_modulado[i:i+50])
            segunda_metade = np.mean(sinal_modulado[i+50:i+100])
            
            # Inverter a lógica de decodificação
            if primeira_metade > 0 and segunda_metade < 0:
                bits.append(1)
            elif primeira_metade < 0 and segunda_metade > 0:
                bits.append(0)
        return bits

    @staticmethod
    def demodular_bipolar(sinal_modulado):
        """Demodulação Bipolar"""
        bits = []
        estado = 1
        for i in range(0, len(sinal_modulado), 100):
            valor_medio = np.mean(sinal_modulado[i:i+100])
            
            if valor_medio == 0:
                bits.append(0)
            elif valor_medio == estado:
                bits.append(1)
                estado = -estado
            else:
                bits.append(1)
                estado = -estado
        return bits

if __name__ == "__main__":
    # Teste das modulações
    bits = [1, 0, 1, 1, 0, 0, 1]
    mod = ModulacaoDigital(bits)
    time = mod.get_time_base()
    
    from src.comunicacao.utils.signal import compare_modulations
    fig = compare_modulations(bits)
    plt.show()