
import os
import argparse
import random
import matplotlib.pyplot as plt


def parse_arguments():

    parser = argparse.ArgumentParser(
        description='Simulación de Ruleta Europea')

    parser.add_argument('-c', '--tiradas', type=int, default=10000,
                        help='Cantidad de tiradas')
    parser.add_argument('-s', '--estrategia', type=str, default='i',
                        help='Estrategia elegida para análisis')
    parser.add_argument('-a', '--capital', type=str, default='f',
                        help='"i": infinito "f" finito')
    parser.add_argument('-i', '--apuesta', type=int, default=18,
                        help='')

    return parser.parse_args()


args = parse_arguments()
cantidad_tiradas = args.tiradas
if args.capital == 'i':
    capital_ini = 0
else:
    capital_ini = int(args.capital)
estrategia = args.estrategia
apuesta = args.apuesta

nro_negros = {1, 3, 5, 7, 9, 12, 14, 16,
              18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
nro_rojos = {2, 4, 6, 8, 10, 11, 13, 15,
             17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

nro_verde = {0}


def tiro():
    return random.randint(0, 36)


def estrategia_fibonacci(capital_ini, apuesta_ini, nro_rojos, tiradas):
    estrategia = "Fibonacci"
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital = []
    historial_apuestas = []
    historial_frecuencia = []
    aciertos = 0
    bancarrota = 0
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89,
           144, 233, 377, 610, 987, 1597, 2584, 4181]
    i = 0
    for _ in range(tiradas):
        apuesta = apuesta_ini * fib[i]
        print(f'tirada:', )
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital < apuesta:
            bancarrota = 1
            break
        resultado = tiro()
        if resultado in nro_rojos:
            aciertos += 1
            capital += apuesta
            i -= 2
            if i < 0:
                i = 0
        else:
            capital -= apuesta
            i += 1
        historial_frecuencia.append(aciertos / (len(historial_frecuencia) + 1))
        print(f'numero: {fib[i]}')
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas, historial_capital,
                        capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)
    graficar_frecuencia_acumulada(historial_frecuencia, estrategia)
    return capital


def estrategia_dAlembert(capital_ini, apuesta_ini, nro_rojos, tiradas):
    estrategia = "dAlembert"
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital = []
    historial_apuestas = []
    historial_frecuencia = []
    aciertos = 0
    bancarrota = 0
    for _ in range(tiradas):
        print(f'tirada:', )
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            bancarrota = 1
            break
        resultado = tiro()
        if resultado in nro_rojos:
            aciertos += 1
            capital += apuesta
            apuesta = max(apuesta_ini, apuesta-apuesta_ini)
        else:
            capital -= apuesta
            apuesta = apuesta + apuesta_ini
        historial_frecuencia.append(aciertos / (len(historial_frecuencia) + 1))
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas, historial_capital,
                        capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)
    graficar_frecuencia_acumulada(historial_frecuencia, estrategia)
    return capital


def estrategia_martingala(capital_ini, apuesta_ini, nro_rojos, tiradas):
    estrategia = "Martingala"
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital = []
    historial_apuestas = []
    historial_frecuencia = []
    aciertos = 0
    bancarrota = 0

    for _ in range(tiradas):
        print(f'tirada:',  tiradas)
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            bancarrota = 1
            print('perdi')
            break
        resultado = tiro()
        if resultado in nro_rojos:
            aciertos += 1
            capital += apuesta
            apuesta = apuesta_ini
        else:

            capital -= apuesta
            apuesta = apuesta*2
        historial_frecuencia.append(aciertos / (len(historial_frecuencia) + 1))
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas, historial_capital,
                        capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)
    graficar_frecuencia_acumulada(historial_frecuencia, estrategia)

    return capital


def estrategia_paroli(capital_ini, apuesta_ini, nro_rojos, tiradas):
    estrategia = "Paroli"
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital = []
    historial_apuestas = []
    historial_frecuencia = []
    aciertos = 0
    bancarrota = 0
    i = 0
    for _ in range(tiradas):
        print(f'tirada:',  tiradas)
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            bancarrota = 1
            print('perdi')
            break
        resultado = tiro()
        if resultado in nro_rojos:
            aciertos += 1
            capital += apuesta
            apuesta = apuesta*2
            i += 1
            if i == 3:
                apuesta = apuesta_ini
                i = 0
        else:
            capital -= apuesta
            apuesta = apuesta_ini
        historial_frecuencia.append(aciertos / (len(historial_frecuencia) + 1))
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas, historial_capital,
                        capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)
    graficar_frecuencia_acumulada(historial_frecuencia, estrategia)

    return capital


def graficar_flujo_caja(num_tiradas, historial_capital, capital_ini, bancarrota, estrategia):
    plt.figure(figsize=(10, 6))

    # Línea horizontal para el capital inicial
    plt.axhline(capital_ini, color='r', linestyle='--',
                label=f'Capital Inicial ({capital_ini})')
    # Línea horizontal en 0 para ver si quebramos
    # plt.axhline(0, color='black', linestyle='--', label=f'Bancarrota {bancarrota}')

    # Creamos el eje X correctamente (de 1 hasta la cantidad de tiradas registradas)
    eje_x = range(1, len(historial_capital) + 1)

    plt.plot(eje_x, historial_capital, label='Capital')

    plt.title(f'Flujo de Caja - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Capital Disponible')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Nos aseguramos de que la carpeta 'image' exista antes de guardar
    os.makedirs('image', exist_ok=True)
    plt.savefig(f'image/flujocaja_{estrategia}.png')
    plt.show()


def graficar_probabilidad_ganar(num_tiradas, historial_capital, capital_ini, bancarrota, estrategia):
    plt.figure(figsize=(10, 6))

    # Línea horizontal para el capital inicial
    plt.axhline(capital_ini, color='r', linestyle='--',
                label=f'Capital Inicial ({capital_ini})')
    # Línea horizontal en 0 para ver si quebramos
    plt.axhline(0, color='black', linestyle='--',
                label=f'Bancarrota {bancarrota}')

    # Creamos el eje X correctamente (de 1 hasta la cantidad de tiradas registradas)
    eje_x = range(1, len(historial_capital) + 1)

    plt.plot(eje_x, historial_capital, label='Capital')

    plt.title(f'Probabilidad Ganar - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Capital Disponible')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Nos aseguramos de que la carpeta 'image' exista antes de guardar
    os.makedirs('image', exist_ok=True)
    plt.savefig(f'image/probabilidad_ganar_{estrategia}.png')
    plt.show()


def graficar_evolucion_apuestas(num_tiradas, historial_apuestas, estrategia):
    plt.figure(figsize=(10, 6))

    # Creamos el eje X correctamente (de 1 hasta la cantidad de tiradas registradas)
    eje_x = range(1, len(historial_apuestas) + 1)

    plt.plot(eje_x, historial_apuestas, label='Apuesta')

    plt.title(f'Evolucion Apuestas - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Apuesta')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Nos aseguramos de que la carpeta 'image' exista antes de guardar
    os.makedirs('image', exist_ok=True)
    plt.savefig(f'image/evolucionapuestas_{estrategia}.png')
    plt.show()


def graficar_frecuencia_acumulada(historial_frecuencia, estrategia):
    plt.figure(figsize=(10, 6))
    prob_teorica = 18/37
    plt.axhline(prob_teorica, color='r', linestyle='--',
                label=f'Probabilidad Teórica ({prob_teorica:.4f})')
    eje_x = range(1, len(historial_frecuencia) + 1)
    plt.bar(eje_x, historial_frecuencia,
            label='Frecuencia Relativa Acumulada', width=0.6)
    plt.title(f'Frecuencia Acumulada de Aciertos - Estrategia: {estrategia}')
    plt.xlabel('Número de Tirada')
    plt.ylabel('Frecuencia Relativa')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs('image', exist_ok=True)
    plt.savefig(f'image/frecuencia_{estrategia}.png')
    plt.show()


def main():

    print(f'Capital: {args.capital}')
    print(f'Estrategia: {args.estrategia}')
    print(f'Cantidad de tiradas: {args.tiradas}')


if __name__ == "__main__":
    main()
if args.estrategia == 'i':
    estrategia_fibonacci(capital_ini, apuesta, nro_rojos, cantidad_tiradas)
if args.estrategia == 'd':
    estrategia_dAlembert(capital_ini, apuesta, nro_rojos, cantidad_tiradas)
if args.estrategia == 'm':
    estrategia_martingala(capital_ini, apuesta, nro_rojos, cantidad_tiradas)
if args.estrategia == 'p':
    estrategia_paroli(capital_ini, apuesta, nro_rojos, cantidad_tiradas)
