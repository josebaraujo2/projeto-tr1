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

### Problemas na Instalação

Caso ocorra problemas na instalação por causa da versão 3.12 do Python, recomendamos a instalação da versão 3.11.11 através do pyenv (Simple Python version management).
1. Instale o [pyenv](https://github.com/pyenv/pyenv).
2. Instale a versão 3.11.11:
```bash
$ pyenv install 3.11.11
```
3. Dentro do repositório clonado, defina a versão local do Python:
```bash
$ pyenv local 3.11.11
```
4. Crie um ambiente virtual:
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```
5. Instale as dependências:
```bash
$ pip install -r requirements.txt
```

## Execução da rotina principal

```bash
cd /home/josebaraujo/tr1/projeto
python3 -m src.Simulador.main
```
ou navegue até o diretorio do Simulador e execute
```bash
python3 main.py
```

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/josebaraujo2/projeto-tr1/issues)