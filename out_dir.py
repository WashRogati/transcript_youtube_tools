"""Pasta de saída padrão: raiz do projeto / out."""
import os

def out_dir():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(d, exist_ok=True)
    return d
