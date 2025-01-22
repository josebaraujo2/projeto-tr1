import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from src.fisica.portadora import ModulacaoPortadora

matplotlib.use('TkAgg') 

def plotar_validacao_modulacoes(bits):
    """
    Plota os sinais modulados com marcações para facilitar a validação
    """
    plt.close('all')  
    mod = ModulacaoPortadora(bits)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 12))
    
    # Plot dos bits originais
    for i, bit in enumerate(bits):
        ax1.plot([i, i+1], [bit, bit], 'b-', linewidth=2)
        ax1.text(i + 0.5, 1.2, str(bit), horizontalalignment='center')
    ax1.set_title('Bits Originais')
    ax1.grid(True)
    ax1.set_ylim(-0.5, 1.5)
    
    # ASK
    tempo_ask, sinal_ask = mod.ask()
    ax2.plot(tempo_ask, sinal_ask, 'b-')
    ax2.set_title('Modulação ASK')
    for i in range(len(bits)):
        ax2.axvline(x=i, color='r', linestyle='--', alpha=0.3)
    ax2.grid(True)
    
    # FSK
    tempo_fsk, sinal_fsk = mod.fsk()
    ax3.plot(tempo_fsk, sinal_fsk, 'b-')
    ax3.set_title('Modulação FSK')
    for i in range(len(bits)):
        ax3.axvline(x=i, color='r', linestyle='--', alpha=0.3)
    ax3.grid(True)
    
    # 8-QAM
    tempo_qam, sinal_qam = mod.qam8()
    ax4.plot(tempo_qam, sinal_qam, 'b-')
    ax4.set_title('Modulação 8-QAM')
    # Adicionar linhas verticais separando os grupos de 3 bits
    num_simbolos = len(bits) // 3 + (1 if len(bits) % 3 != 0 else 0)
    for i in range(num_simbolos):
        ax4.axvline(x=i, color='r', linestyle='--', alpha=0.3)
    ax4.grid(True)
    
    # Ajustar layout e mostrar
    plt.tight_layout()
    plt.show(block=True)  
    return fig

if __name__ == "__main__":
    # Sequência de teste
    bits = [1, 0, 1, 1, 0, 0, 1]
    print("Validando modulações para sequência:", bits)
    
    try:
        fig = plotar_validacao_modulacoes(bits)
        print("Gráficos gerados com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar gráficos: {e}")
        print("Tente instalar os pacotes necessários:")
        print("pip install matplotlib numpy")