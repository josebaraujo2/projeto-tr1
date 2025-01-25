# Simulador de Protocolos de Rede

Simulador para demonstração do funcionamento da camada de enlace e camada física, implementando protocolos de enquadramento, modulação banda-base e modulação por portadora.

## Requisitos

- Python 3.8+
- GTK 3.0
- Bibliotecas Python listadas em _requirements.txt_

### Dependências do Sistema (Ubuntu / WSL)

```bash
$ sudo apt update
$ sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev python3.12-venv
```

### Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

3. Instale as dependências:
```bash
$ pip install -r requirements.txt
```

## Execução

```bash
$ python main.py transmitter  # em um terminal
$ python main.py receiver     # em outro terminal
```

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/josebaraujo2/projeto-tr1/issues)