import numpy as np
import matplotlib.pyplot as plt

class ModulacaoDigital:
    def __init__(self, bits):
        self.bits = bits
        self.sampling_rate = 100  
        
    def _generate_time_base(self):
        """Gera base de tempo para os sinais"""
        return np.linspace(0, len(self.bits), len(self.bits) * self.sampling_rate)
    
    def nrz_polar(self):
        """
        Modulação NRZ-Polar
        1 -> Tensão positiva
        0 -> Tensão negativa
        """
        signal = []
        for bit in self.bits:
            # Gera sampling_rate pontos para cada bit
            level = 1 if bit == 1 else -1
            signal.extend([level] * self.sampling_rate)
        
        return np.array(signal)
    
    def manchester(self):
        """
        Modulação Manchester
        1 -> Transição negativa para positiva
        0 -> Transição positiva para negativa
        """
        signal = []
        for bit in self.bits:
            if bit == 1:
                # Primeira metade positiva, segunda metade negativa
                signal.extend([1] * (self.sampling_rate//2))
                signal.extend([-1] * (self.sampling_rate//2))
            else:
                # Primeira metade negativa, segunda metade positiva
                signal.extend([-1] * (self.sampling_rate//2))
                signal.extend([1] * (self.sampling_rate//2))
        
        return np.array(signal)
    
    def bipolar(self):
        """
        Modulação Bipolar (AMI)
        1 -> Alternância entre tensão positiva e negativa
        0 -> Zero volts
        """
        signal = []
        last_polarity = 1  # Começa com polaridade positiva
        
        for bit in self.bits:
            if bit == 0:
                signal.extend([0] * self.sampling_rate)
            else:
                # Alterna entre +1 e -1 para cada '1'
                signal.extend([last_polarity] * self.sampling_rate)
                last_polarity = -last_polarity
        
        return np.array(signal)

    def get_time_base(self):
        """Retorna base de tempo para plotagem"""
        return self._generate_time_base()

if __name__ == "__main__":
    # Teste das modulações
    bits = [1, 0, 1, 1, 0, 0, 1]
    mod = ModulacaoDigital(bits)
    time = mod.get_time_base()
    
    from src.comunicacao.utils.signal import compare_modulations
    fig = compare_modulations(bits)
    plt.show()