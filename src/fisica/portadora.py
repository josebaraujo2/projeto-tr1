import numpy as np
import matplotlib.pyplot as plt

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
        bits_padded = self.bits.copy()
        if len(bits_padded) % 3 != 0:
            padding = 3 - (len(bits_padded) % 3)
            bits_padded.extend([0] * padding)
            
        estados_qam = {
            (0,0,0): (1.0, 0),
            (0,0,1): (1.0, np.pi/4),
            (0,1,0): (1.0, np.pi/2),
            (0,1,1): (1.0, 3*np.pi/4),
            (1,0,0): (2.0, 0),
            (1,0,1): (2.0, np.pi/4),
            (1,1,0): (2.0, np.pi/2),
            (1,1,1): (2.0, 3*np.pi/4)
        }
        
        # Calcular o número de símbolos e tempo total
        num_simbolos = len(bits_padded) // 3
        tempo_total = num_simbolos
        amostras_por_simbolo = self.amostras_por_bit
        
        # Gerar base de tempo específica para QAM
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
            
            # Janela de suavização
            janela = np.ones(amostras_por_simbolo)
            janela[:50] = np.linspace(0, 1, 50)
            janela[-50:] = np.linspace(1, 0, 50)
            
            # Gerar componentes I e Q
            sinal_i = amplitude * np.cos(2 * np.pi * self.freq_portadora * t_simbolo + fase)
            sinal_q = amplitude * np.sin(2 * np.pi * self.freq_portadora * t_simbolo + fase)
            
            # Aplicar janela
            sinal[inicio:fim] = (sinal_i + sinal_q) * janela
        
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