import statistics


def calcular_frecuencia_acumulada(resultados, numero_elegido):
    acumulada = []
    contador = 0
    for i, r in enumerate(resultados):
        if r == numero_elegido:
            contador += 1
        acumulada.append(contador / (i + 1))
    return acumulada


def calcular_media_acumulada(resultados):
    acumulada = []
    suma = 0
    for i, r in enumerate(resultados):
        suma += r
        acumulada.append(suma / (i + 1))
    return acumulada


def calcular_varianza_acumulada(resultados):
    acumulada = []
    suma = 0
    suma_cuadrados = 0
    for i, r in enumerate(resultados):
        n = i + 1
        suma += r
        suma_cuadrados += r ** 2
        if n >= 2:
            media = suma / n
            varianza = (suma_cuadrados - n * media ** 2) / (n - 1)
        else:
            varianza = 0
        acumulada.append(varianza)
    return acumulada


def calcular_desvio_acumulado(resultados):
    varianzas = calcular_varianza_acumulada(resultados)
    return [v ** 0.5 for v in varianzas]
