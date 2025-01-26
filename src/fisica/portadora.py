import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

class ModulacaoPortadora:
    def __init__(self, bits, freq_portadora=20):
        self.bits = bits
        self.freq_portadora = freq_portadora
        self.taxa_amostragem = 500
        self.amostras_por_bit = self.taxa_amostragem
        self.tempo_total = len(self.bits)
        
    def _gerar_base_tempo(self):
        num_amostras = len(self.bits) * self.amostras_por_bit
        return np.linspace(0, self.tempo_total, num_amostras)
    
    def ask(self):
        tempo = self._gerar_base_tempo()
        portadora = np.sin(2 * np.pi * self.freq_portadora * tempo)
        sinal = np.zeros_like(tempo)
        
        for i, bit in enumerate(self.bits):
            inicio = i * self.amostras_por_bit
            fim = (i + 1) * self.amostras_por_bit
            
            amplitude = 1.0 if bit == 1 else 0.3
            janela = np.ones(self.amostras_por_bit)
            janela[:50] = np.linspace(0, 1, 50)
            janela[-50:] = np.linspace(1, 0, 50)
            
            sinal[inicio:fim] = amplitude * portadora[inicio:fim] * janela
            
        return tempo, sinal
    
    def fsk(self):
        tempo = self._gerar_base_tempo()
        sinal = np.zeros_like(tempo)
        
        freq_alta = self.freq_portadora * 1.2
        freq_baixa = self.freq_portadora * 0.8
        
        for i, bit in enumerate(self.bits):
            inicio = i * self.amostras_por_bit
            fim = (i + 1) * self.amostras_por_bit
            
            freq = freq_alta if bit == 1 else freq_baixa
            t_bit = tempo[inicio:fim] - tempo[inicio]
            sinal[inicio:fim] = np.sin(2 * np.pi * freq * t_bit)
            
            if i > 0:
                trans_inicio = inicio
                trans_fim = inicio + 50
                alpha = np.linspace(0, 1, trans_fim - trans_inicio)
                sinal[trans_inicio:trans_fim] = (
                    alpha * sinal[trans_inicio:trans_fim] +
                    (1 - alpha) * sinal[trans_inicio-1]
                )
                
        return tempo, sinal
    
    def qam8(self):
        """8-QAM com transições suaves entre símbolos"""
        # Garantir que o número de bits é múltiplo de 3
        estados_qam = {
        (0,0,0): (0.5, 0),      # Low amplitude, 0 phase
        (0,0,1): (0.5, np.pi/4),
        (0,1,0): (0.5, np.pi/2),
        (0,1,1): (0.5, 3*np.pi/4),
        (1,0,0): (1.5, 0),      # High amplitude, 0 phase
        (1,0,1): (1.5, np.pi/4),
        (1,1,0): (1.5, np.pi/2),
        (1,1,1): (1.5, 3*np.pi/4)
        }
        
        bits_padded = self.bits.copy()
        if len(bits_padded) % 3 != 0:
            padding = 3 - (len(bits_padded) % 3)
            bits_padded.extend([0] * padding)
        
        num_simbolos = len(bits_padded) // 3
        tempo_total = num_simbolos
        amostras_por_simbolo = self.taxa_amostragem
        
        num_amostras_total = num_simbolos * amostras_por_simbolo
        tempo = np.linspace(0, tempo_total, num_amostras_total)
        sinal = np.zeros_like(tempo)
        
        for i in range(0, len(bits_padded), 3):
            simbolo = tuple(bits_padded[i:i+3])
            amplitude, fase = estados_qam[simbolo]
            
            idx_simbolo = i // 3
            inicio = idx_simbolo * amostras_por_simbolo
            fim = (idx_simbolo + 1) * amostras_por_simbolo
            
            t_simbolo = tempo[inicio:fim] - tempo[inicio]
            
            sinal[inicio:fim] = amplitude * np.cos(2 * np.pi * self.freq_portadora * t_simbolo + fase)
        
        return tempo, sinal

    def plotar_modulacao(self, tipo_modulacao):
        if tipo_modulacao.lower() == 'ask':
            tempo, sinal = self.ask()
            titulo = 'Modulação ASK'
        elif tipo_modulacao.lower() == 'fsk':
            tempo, sinal = self.fsk()
            titulo = 'Modulação FSK'
        elif tipo_modulacao.lower() == '8qam':
            tempo, sinal = self.qam8()
            titulo = 'Modulação 8-QAM'
        else:
            raise ValueError("Tipo de modulação inválido")
            
        plt.figure(figsize=(12, 4))
        plt.plot(tempo, sinal)
        plt.title(titulo)
        plt.xlabel('Tempo')
        plt.ylabel('Amplitude')
        plt.grid(True)
        plt.show()

    @staticmethod
    def demodular_ask(tempo, sinal, freq_portadora=20):
        """Demodulação ASK com método de envelope"""
        # Calcular envelope do sinal
        envelope = np.abs(sinal)
        
        # Encontrar threshold adaptativo
        threshold = np.median(envelope)
        
        # Demodulação baseada no envelope
        bits = [1 if np.mean(envelope[i:i+500]) > threshold else 0 
                for i in range(0, len(envelope), 500)]
        return bits

    @staticmethod
    def demodular_fsk(tempo, sinal, freq_portadora=20):
        """Demodulação FSK"""
        freq_alta = freq_portadora * 1.2
        freq_baixa = freq_portadora * 0.8
        
        sinal_alta = np.sin(2 * np.pi * freq_alta * tempo)
        sinal_baixa = np.sin(2 * np.pi * freq_baixa * tempo)
        
        energia_alta = [np.mean(sinal[i:i+500] * sinal_alta[i:i+500])
                        for i in range(0, len(sinal), 500)]
        energia_baixa = [np.mean(sinal[i:i+500] * sinal_baixa[i:i+500])
                        for i in range(0, len(sinal), 500)]
        
        bits = [1 if alta > baixa else 0 
                for alta, baixa in zip(energia_alta, energia_baixa)]
        return bits

    @staticmethod
    def demodular_qam8_refinado(tempo, sinal, freq_portadora=20, amostras_por_simbolo=500):
        """Demodulação robusta para 8-QAM com refinamento de amplitude e fase."""
        num_simbolos = len(sinal) // amostras_por_simbolo
        bits = []

        # Gerar portadoras em fase e quadratura
        t_simbolo = np.linspace(0, 1, amostras_por_simbolo, endpoint=False)
        portadora_cos = np.cos(2 * np.pi * freq_portadora * t_simbolo)
        portadora_sin = np.sin(2 * np.pi * freq_portadora * t_simbolo)

        for i in range(num_simbolos):
            # Extrair o sinal do símbolo
            simbolo_sinal = sinal[i * amostras_por_simbolo:(i + 1) * amostras_por_simbolo]

            # Correlacionar com as portadoras
            componente_i = 2 * np.sum(simbolo_sinal * portadora_cos) / amostras_por_simbolo
            componente_q = 2 * np.sum(simbolo_sinal * portadora_sin) / amostras_por_simbolo

            # Converter para coordenadas polares
            amplitude = np.sqrt(componente_i**2 + componente_q**2)
            fase = np.arctan2(componente_q, componente_i)

            # Normalizar a fase para o intervalo [0, 2pi)
            if fase < 0:
                fase += 2 * np.pi

            # Determinar os bits de amplitude
            bit_amplitude = 1 if amplitude > 1.0 else 0

            # Determinar os bits de fase (mapear quadrantes)
            if 0 <= fase < np.pi / 4 or 7 * np.pi / 4 <= fase < 2 * np.pi:
                bit_i, bit_q = 0, 0
            elif np.pi / 4 <= fase < 3 * np.pi / 4:
                bit_i, bit_q = 0, 1
            elif 3 * np.pi / 4 <= fase < 5 * np.pi / 4:
                bit_i, bit_q = 1, 1
            else:
                bit_i, bit_q = 1, 0

            # Adicionar bits à lista
            bits.extend([bit_i, bit_q, bit_amplitude])

        # Retornar somente os bits relevantes
        return bits[:num_simbolos * 3]