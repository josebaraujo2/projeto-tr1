import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from src.comunicacao.transmissor import TransmitterWindow
from src.comunicacao.receptor import ReceiverWindow

def print_usage():
    print("Uso: python main.py [transmissor|receptor]")
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print_usage()
    
    mode = sys.argv[1].lower()
    
    if mode == "transmissor":
        window = TransmitterWindow()
    elif mode == "receptor":
        window = ReceiverWindow()
    else:
        print_usage()
    
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()