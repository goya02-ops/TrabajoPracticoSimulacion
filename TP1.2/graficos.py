import os
import matplotlib.pyplot as plt

from constantes import PROB_ROJO


def graficar_flujo_caja(historial_capital, capital_ini, estrategia):
    plt.figure(figsize=(10, 6))
    if capital_ini != float('inf'):
        plt.axhline(capital_ini, color='r', linestyle='--',
                    label=f'Capital Inicial ({capital_ini})')
    eje_x = range(1, len(historial_capital) + 1)
    plt.plot(eje_x, historial_capital, label='Capital')
    plt.title(f'Flujo de Caja - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Capital Disponible')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(f'image/{estrategia}', exist_ok=True)
    plt.savefig(f'image/{estrategia}/flujocaja_{estrategia}.png')
    plt.show()


def graficar_evolucion_apuestas(historial_apuestas, estrategia):
    plt.figure(figsize=(10, 6))
    eje_x = range(1, len(historial_apuestas) + 1)
    plt.plot(eje_x, historial_apuestas, label='Apuesta')
    plt.title(f'Evolucion Apuestas - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Apuesta')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(f'image/{estrategia}', exist_ok=True)
    plt.savefig(f'image/{estrategia}/evolucionapuestas_{estrategia}.png')
    plt.show()


def graficar_frecuencia_acumulada(historial_frecuencia, estrategia):
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
    os.makedirs(f'image/{estrategia}', exist_ok=True)
    plt.savefig(f'image/{estrategia}/frecuencia_{estrategia}.png')
    plt.show()
