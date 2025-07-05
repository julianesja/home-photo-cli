# Parser de argumentos de línea de comandos

import argparse

def get_parser():
    parser = argparse.ArgumentParser(description="Procesador de imágenes con reconocimiento facial")
    parser.add_argument('--input', type=str, help='Carpeta de entrada de imágenes')
    parser.add_argument('--output', type=str, help='Carpeta de salida para imágenes procesadas')
    return parser 