import matplotlib.pyplot as plt
from TP1.CONSTANTES import NUMERO_RULETA
import random

RUTA_GUARDADO = 'graficas/'


def simular_apuestas(cantidad_tiradas, numero_elegido=18, saldo_inicial=1000, apuesta=1):
    saldo = saldo_inicial
    saldos = [saldo]
    for _ in range(cantidad_tiradas):
        numero = random.choice(NUMERO_RULETA)
        saldo -= apuesta
        if numero == numero_elegido:
            saldo += 36 * apuesta
        saldos.append(saldo)
    return saldos


def graficar_evolucion_capital(saldos):
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(saldos)), saldos, label='Saldo del jugador')
    plt.axhline(y=saldos[0], color='g', linestyle='--', label='Saldo inicial')
    plt.title('Evolución del capital en apuestas al número elegido')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Saldo')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/evolucion_capital.png')
    plt.show()
