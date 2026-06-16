import random


def uniforme_inversa(a, b, size=1):

    valores = []
    for _ in range(size):

        r = random.random()
        x = a + (b - a) * r
        valores.append(x)

    return valores


muestras = uniforme_inversa(10, 20, 5)
print(muestras)
