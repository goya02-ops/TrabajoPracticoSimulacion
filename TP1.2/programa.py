import argparse

from estrategias import (
    estrategia_fibonacci,
    estrategia_dAlembert,
    estrategia_martingala,
    estrategia_paroli,
)
from graficos import graficador

ESTRATEGIAS = {
    'i': estrategia_fibonacci,
    'd': estrategia_dAlembert,
    'm': estrategia_martingala,
    'p': estrategia_paroli,
}

NOMBRES = {
    'i': 'Fibonacci',
    'd': 'dAlembert',
    'm': 'Martingala',
    'p': 'Paroli',
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Simulación de Ruleta Europea')
    parser.add_argument('-c', '--tiradas', type=int, default=10000,
                        help='Cantidad de tiradas')
    parser.add_argument('-s', '--estrategia', type=str, default='i',
                        help='Estrategia: i Fibonacci, d dAlembert, m Martingala, p Paroli')
    parser.add_argument('-a', '--capital', type=str, default='10000',
                        help='Capital inicial: "i" para infinito, o un número para finito')
    parser.add_argument('-i', '--apuesta', type=int, default=18,
                        help='Apuesta inicial')
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.estrategia not in ESTRATEGIAS:
        print(f'Estrategia inválida: {args.estrategia}')
        return

    # Capital infinito o acotado
    if args.capital == 'i':
        # Si el capital es infinito, lo tratamos como 0 para el flujo de caja, pero sin riesgo de bancarrota
        capital_ini = float('inf')
    else:
        capital_ini = int(args.capital)

    nombre = NOMBRES[args.estrategia]
    estrategia_fn = ESTRATEGIAS[args.estrategia]

    print(f'Estrategia: {nombre}')
    print(
        f'Capital inicial: {"infinito" if capital_ini == float("inf") else capital_ini}')
    print(f'Apuesta inicial: {args.apuesta}')
    print(f'Tiradas: {args.tiradas}')

    resultado = estrategia_fn(capital_ini, args.apuesta, args.tiradas)

    graficador(capital_ini, nombre, resultado)


if __name__ == "__main__":
    main()
