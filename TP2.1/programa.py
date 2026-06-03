import random
from tests import test_chi_cuadrado, test_rachas


def GCL(seed, multiplo, incremento, modulo, iteraciones):

    if iteraciones <= 0 or iteraciones > modulo:
        return "El número de iteraciones debe ser mayor que 0 y menor o igual al módulo."

    a = multiplo
    c = incremento
    m = modulo
    i = iteraciones
    for _ in range(i):
        seed = (a * seed + c) % m
        yield seed / m


def mid_square(seed, iteraciones):
    if iteraciones <= 0:
        return "El número de iteraciones debe ser mayor que 0."

    seed = "00" + str(seed) + "00"
    for _ in range(iteraciones):

        seed_str = str(seed).zfill(8)
        mid_digits = seed_str[2:6]
        seed = int(mid_digits) ** 2
        yield seed / 10 ** 8


def built_in_random(iteraciones):
    if iteraciones <= 0:
        return "El número de iteraciones debe ser mayor que 0."

    for _ in range(iteraciones):
        yield random.random()


if __name__ == "__main__":

    print("GLC")
    numerosGLC = list(GCL(1234, 1103515245, 12345, 2**64, 100))
    test_chi_cuadrado(numerosGLC, num_celdas=10, alfa=0.01)
    test_rachas(numerosGLC, alfa=0.01)

    print("\nMid Square")
    numerosMidSquare = list(mid_square(9731, 100))
    test_chi_cuadrado(numerosMidSquare, num_celdas=10, alfa=0.01)
    test_rachas(numerosMidSquare, alfa=0.01)

    print("\nBuilt-in Random")
    numerosBuiltInRandom = list(built_in_random(100))
    test_chi_cuadrado(numerosBuiltInRandom, num_celdas=10, alfa=0.01)
    test_rachas(numerosBuiltInRandom, alfa=0.01)
