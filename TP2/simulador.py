import argparse
import random
import matplotlib.pyplot as plt

def parse_arguments():

    parser = argparse.ArgumentParser(
        description='Simulación de Ruleta Europea')

    parser.add_argument('-c', '--tiradas', type=int, default=10000,
                        help='Cantidad de tiradas por corrida')
    parser.add_argument('-n', '--corridas', type=int, default=200,
                        help='Cantidad de corridas para la distribución de medias')
    parser.add_argument('-e', '--elegido', type=int, default=18,
                        help='Número elegido para análisis')
    parser.add_argument('-s', '--estrategia', type=int, default=18,
                        help='Estrategia elegida para análisis')
    parser.add_argument('-a', '--capital', type=int, default=18,
                        help='"i": infinito "f" finito')
    
    return parser.parse_args()

nro_negros = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
nro_rojos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

nro_verde = {0}

def tiro():
    return random.randint(0,36)

def estrategia_fibonacci(capital_ini, apuesta_ini,nro_rojos, tiradas):
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    fib = [1,1,2,3,5,8,13,21,34,55,89,144]
    i = 0
    for _ in range(tiradas):
        print(f'tirada:', )
        historial_capital.append(capital)
        print(historial_capital)
        if capital <= 0:
            break
        elif tiro() in nro_rojos:
            capital+=apuesta
            apuesta = apuesta_ini
        else:
            capital-=apuesta
            apuesta = apuesta * fib[i]
            i+=1
        print(f'Capital final: {capital}')
        
    return capital

def estrategia_dAlembert(capital_ini, apuesta_ini,nro_rojos, tiradas):
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    for _ in range(tiradas):
        print(f'tirada:', )
        historial_capital.append(capital)
        print(historial_capital)
        if capital <= 0:
            break
        elif tiro() in nro_rojos:
            capital+=apuesta
            apuesta = max(apuesta_ini, apuesta-apuesta_ini)
        else:
            capital-=apuesta
            apuesta = apuesta + apuesta_ini

        print(f'Capital final: {capital}')
        
    return capital
    
def estrategia_martingala(capital_ini, apuesta_ini,nro_rojos, tiradas):
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]

    for _ in range(tiradas):
        print(f'tirada:',  tiradas )
        historial_capital.append(capital)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
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
        
    return capital

def estrategia_paroli(capital_ini, apuesta_ini,nro_rojos, tiradas):
    capital = capital_ini
    apuesta = apuesta_ini
    historial_capital =[]
    i=0
    for _ in range(tiradas):
        print(f'tirada:',  tiradas )
        historial_capital.append(capital)
        print(historial_capital)
        if capital <= 0 or capital < apuesta:
            print('perdi')
            break
        elif tiro() in nro_rojos:
            i+=1
            capital+=apuesta
            apuesta = apuesta*2
            if i==2:
                apuesta = apuesta_ini
                i=0
        else:
            capital -= apuesta
            apuesta = apuesta_ini
        print(f'apuesta: {apuesta}')
        print(f'Capital final: {capital}')
        
    return capital


def main():
    # 1. Obtener parámetros del usuario
    args = parse_arguments()
    cantidad_tiradas = args.tiradas
    numero_elegido = args.elegido
    num_corridas = args.corridas
    capital_ini= args.capital
    estrategia= args.estrategia


    print(f'Capital: {args.capital}')
    print(f'Estrategia: {args.estrategia}')
    print(f'Cantidad de tiradas: {args.tiradas}')
    print(f'Número elegido: {args.elegido}')
    print(f'Cantidad de corridas: {args.corridas}')
    
    
if __name__ == "__main__":
    main()
    estrategia_paroli(1000,20,nro_rojos,1000)
    