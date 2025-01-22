import matplotlib.pyplot as plt
import numpy as np

def plot_digital_signal(time, signal, title, ax=None):
    """
    Plota um sinal digital
    
    Args:
        time: array com base de tempo
        signal: array com o sinal
        title: título do gráfico
        ax: eixo do matplotlib (opcional)
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))
    
    ax.plot(time, signal, 'b-', linewidth=2)
    ax.grid(True)
    ax.set_ylim([-1.5, 1.5])
    ax.set_title(title)
    ax.set_xlabel('Tempo')
    ax.set_ylabel('Amplitude')
    
    return ax

def compare_modulations(bits):
    """
    Compara diferentes modulações para a mesma sequência de bits
    
    Args:
        bits: lista de bits a serem modulados
    """
    from src.fisica.digital import ModulacaoDigital
    
    mod = ModulacaoDigital(bits)
    time = mod.get_time_base()
    
    # Cria figura com três subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))
    
    # Plota cada modulação
    plot_digital_signal(time, mod.nrz_polar(), 'NRZ-Polar', ax1)
    plot_digital_signal(time, mod.manchester(), 'Manchester', ax2)
    plot_digital_signal(time, mod.bipolar(), 'Bipolar', ax3)
    
    plt.tight_layout()
    return fig