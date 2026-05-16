import os
import matplotlib.pyplot as plt

from constantes import PROB_ROJO

RUTA = 'image'
RUTA_INFINITO = RUTA + '/infinito'
RUTA_ACOTADO = RUTA + '/acotado'


def graficar_flujo_caja(historial_capital, capital_ini, estrategia, RUTA_GUARDADO):
    plt.figure(figsize=(10, 6))
    if capital_ini == float('inf'):
        # Si el capital es infinito, mostramos una línea de referencia en 0 para indicar que no hay límite de capital, pero el flujo de caja se muestra normalmente.
        plt.axhline(0, color='r', linestyle='--',
                    label=f'Capital Inicial (Infinito)')
        RUTA_GUARDADO = RUTA_INFINITO
    else:
        plt.axhline(capital_ini, color='r', linestyle='--',
                    label=f'Capital Inicial ({capital_ini})')
        RUTA_GUARDADO = RUTA_ACOTADO
    eje_x = range(1, len(historial_capital) + 1)
    plt.plot(eje_x, historial_capital, label='Capital')
    plt.title(f'Flujo de Caja - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Capital Disponible')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(f'{RUTA_GUARDADO}/{estrategia}', exist_ok=True)
    plt.savefig(f'{RUTA_GUARDADO}/{estrategia}/flujocaja_{estrategia}.png')
    plt.show()


def graficar_evolucion_apuestas(historial_apuestas, estrategia, RUTA_GUARDADO):
    plt.figure(figsize=(10, 6))
    eje_x = range(1, len(historial_apuestas) + 1)
    plt.plot(eje_x, historial_apuestas, label='Apuesta')
    plt.title(f'Evolucion Apuestas - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Apuesta')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f'{RUTA_GUARDADO}/{estrategia}/evolucionapuestas_{estrategia}.png')
    plt.show()


def graficar_frecuencia_acumulada(historial_frecuencia, estrategia, RUTA_GUARDADO):
    plt.figure(figsize=(10, 6))
    plt.axhline(PROB_ROJO, color='r', linestyle='--',
                label=f'Probabilidad Teórica ({PROB_ROJO:.4f})')
    eje_x = range(1, len(historial_frecuencia) + 1)
    plt.bar(eje_x, historial_frecuencia,
            label='Frecuencia Relativa Acumulada', width=0.6)
    plt.title(f'Frecuencia Acumulada de Aciertos - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Frecuencia Relativa')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/{estrategia}/frecuencia_{estrategia}.png')
    plt.show()


def graficador(capital_ini, estrategia, resultado: dict):
    historial_capital = resultado['historial_capital']
    historial_apuestas = resultado['historial_apuestas']
    historial_frecuencia = resultado['historial_frecuencia']

    if capital_ini == float('inf'):
        RUTA_GUARDADO = RUTA_INFINITO
    else:
        RUTA_GUARDADO = RUTA_ACOTADO
    os.makedirs(f'{RUTA_GUARDADO}/{estrategia}', exist_ok=True)
    graficar_flujo_caja(historial_capital, capital_ini,
                        estrategia, RUTA_GUARDADO)
    graficar_evolucion_apuestas(historial_apuestas, estrategia, RUTA_GUARDADO)
    graficar_frecuencia_acumulada(
        historial_frecuencia, estrategia, RUTA_GUARDADO)
