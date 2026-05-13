
from matplotlib import backend_bases
import enum
from matplotlib import figure
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
    capital_ini = float('inf')
else:
    capital_ini = int(args.capital)
estrategia= args.estrategia
apuesta = args.apuesta

nro_negros = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
nro_rojos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

nro_verde = {0}

def tiro():
    return random.randint(0,36)

def estrategia_fibonacci(capital_ini, apuesta_ini,nro_rojos, tiradas):
    estrategia="Fibonacci" #MODIFCAR
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    historial_apuestas = []
    bancarrota = 0
    fib = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584,4181]
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
        elif tiro() in nro_rojos:
            capital+=apuesta
            i-=2
            if i < 0:
                i=0
        else:
            capital-=apuesta
            i+=1
        print(f'numero: {fib[i]}')
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas ,historial_capital,capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)   
    return capital

def estrategia_dAlembert(capital_ini, apuesta_ini,nro_rojos, tiradas):
    estrategia="dAlembert" #MODIFCAR
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    historial_apuestas = []
    bancarrota = 0
    for _ in range(tiradas):
        print(f'tirada:', )
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            bancarrota = 1
            break
        elif tiro() in nro_rojos:
            capital+=apuesta
            apuesta = max(apuesta_ini, apuesta-apuesta_ini)
        else:
            capital-=apuesta
            apuesta = apuesta + apuesta_ini

        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas ,historial_capital,capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)     
    return capital
    
def estrategia_martingala(capital_ini, apuesta_ini,nro_rojos, tiradas):
    estrategia="Martingala" #MODIFCAR
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    historial_apuestas = []
    bancarrota = 0

    for _ in range(tiradas):
        print(f'tirada:',  tiradas )
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            bancarrota = 1
            print('perdi')
            break
        elif tiro() in nro_rojos:
            capital+=apuesta
            apuesta = apuesta_ini
        else:
    
            capital -= apuesta
            apuesta = apuesta*2
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas ,historial_capital,capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)   
        
    return capital

def estrategia_paroli(capital_ini, apuesta_ini,nro_rojos, tiradas):
    estrategia="Paroli" #MODIFCAR
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    historial_apuestas = []
    bancarrota = 0
    i=0
    for _ in range(tiradas):
        print(f'tirada:',  tiradas )
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            print('perdi')
            break
        elif tiro() in nro_rojos:
            capital+=apuesta
            apuesta = apuesta*2
            i+=1
            if i==3:
                apuesta = apuesta_ini
                i=0
        else:
            capital -= apuesta
            apuesta = apuesta_ini
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
    graficar_flujo_caja(tiradas ,historial_capital,capital_ini, bancarrota, estrategia)
    graficar_evolucion_apuestas(tiradas, historial_apuestas, estrategia)   
        
    return capital

import os

def graficar_flujo_caja(num_tiradas, historial_capital, capital_ini, bancarrota, estrategia):
    plt.figure(figsize=(10, 6))
    
    # Línea horizontal para el capital inicial
    plt.axhline(capital_ini, color='r', linestyle='--', label=f'Capital Inicial ({capital_ini})')
    # Línea horizontal en 0 para ver si quebramos
    #plt.axhline(0, color='black', linestyle='--', label=f'Bancarrota {bancarrota}')
    
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
    plt.axhline(capital_ini, color='r', linestyle='--', label=f'Capital Inicial ({capital_ini})')
    # Línea horizontal en 0 para ver si quebramos
    plt.axhline(0, color='black', linestyle='--', label=f'Bancarrota {bancarrota}')
    
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

def main():
    # 1. Obtener parámetros del usuario



    print(f'Capital: {args.capital}')
    print(f'Estrategia: {args.estrategia}')
    print(f'Cantidad de tiradas: {args.tiradas}')
    
    
if __name__ == "__main__":
    main()
if args.estrategia == 'i':
    estrategia_fibonacci(capital_ini,apuesta,nro_rojos,cantidad_tiradas)
if args.estrategia == 'd':
    estrategia_dAlembert(capital_ini,apuesta,nro_rojos,cantidad_tiradas)
if args.estrategia == 'm':
    estrategia_martingala(capital_ini,apuesta,nro_rojos,cantidad_tiradas)
if args.estrategia == 'p':
    estrategia_paroli(capital_ini,apuesta,nro_rojos,cantidad_tiradas)
 

    