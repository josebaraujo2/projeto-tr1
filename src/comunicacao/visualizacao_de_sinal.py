import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure

class SignalVisualizationWindow(Gtk.Window):
    def __init__(self, title="Visualização do Sinal"):
        super().__init__(title=title)
        self.set_default_size(800, 600)
        
        # Layout principal
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)
        
        # Área do gráfico
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.box.pack_start(self.canvas, True, True, 0)
        
        # Botões de controle
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_start(10)
        button_box.set_margin_end(10)
        button_box.set_margin_bottom(10)
        self.box.pack_start(button_box, False, False, 0)
        
        # Botão para fechar
        close_button = Gtk.Button(label="Fechar")
        close_button.connect("clicked", lambda w: self.destroy())
        button_box.pack_end(close_button, False, False, 0)
        
    def plot_signal(self, signal, signal_type="NRZ-Polar"):
        """Plot the signal with proper formatting"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if isinstance(signal, list):
            ax.plot(signal, marker='o')
        else:
            ax.plot(signal)
            
        ax.set_title(f"Sinal {signal_type}")
        ax.grid(True)
        self.canvas.draw()
        
    def plot_comparison(self, original, decoded, modulation_type):
        """Plot comparison between original and decoded signals"""
        self.figure.clear()
        
        # Plot original vs decoded
        ax1 = self.figure.add_subplot(211)
        ax1.plot(original, label='Original', marker='o')
        ax1.plot(decoded, label='Decodificado', marker='x')
        ax1.set_title(f"{modulation_type} - Original vs Decodificado")
        ax1.legend()
        ax1.grid(True)
        
        # Plot errors
        ax2 = self.figure.add_subplot(212)
        errors = [i for i in range(len(original)) if original[i] != decoded[i]]
        error_positions = [1 if i in errors else 0 for i in range(len(original))]
        ax2.plot(error_positions, 'r')
        ax2.set_title("Posições de Erro")
        ax2.grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()