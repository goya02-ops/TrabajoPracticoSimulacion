import matplotlib.pyplot as plt
import numpy as np


def numeros_a_bitmap(numeros):
    """Convierte una lista de números a una matriz cuadrada de bits (0 y 1).
    Usa el mayor cuadrado perfecto posible con los datos disponibles."""
    bits = np.array([1 if x >= 0.5 else 0 for x in numeros])
    lado = int(np.sqrt(len(bits)))
    return bits[:lado * lado].reshape(lado, lado)


def guardar_imagen_bits(numeros, nombre, nombre_archivo):
    """Genera y guarda la imagen de bits estilo RANDOM.ORG para un generador."""
    bitmap = numeros_a_bitmap(numeros)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(bitmap, cmap='gray', vmin=0, vmax=1, interpolation='nearest')
    ax.axis('off')
    ax.set_title(nombre, fontsize=13, fontweight='bold', pad=10)

    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> Guardado: {nombre_archivo}")


def generar_graficas(numerosGLC, numerosMidSquare, numerosBuiltInRandom):
    """Genera las imágenes con los mismos números usados en los tests."""
    generadores = [
        (numerosGLC,            'GCL',            'bits_gcl.png'),
        (numerosMidSquare,      'Mid Square',      'bits_midsquare.png'),
        (numerosBuiltInRandom,  'Built-in Random', 'bits_builtin.png'),
    ]
    for numeros, nombre, archivo in generadores:
        guardar_imagen_bits(numeros, nombre, archivo)

