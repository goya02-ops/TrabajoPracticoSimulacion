import random

from calculos import (
    calcular_frecuencia_acumulada,
    calcular_media_acumulada,
    calcular_varianza_acumulada,
    calcular_desvio_acumulado,
)
from CONSTANTES import NUMERO_RULETA


def simular_tiradas(cantidad_tiradas):
    return [random.choice(NUMERO_RULETA) for _ in range(cantidad_tiradas)]


def simular_multiples_corridas(num_corridas, tiradas_por_corrida, numero_elegido):
    medias = []
    for _ in range(num_corridas):
        resultados = simular_tiradas(tiradas_por_corrida)
        medias.append(calcular_media_acumulada(resultados)[-1])
    return medias


def simular_todas_corridas(num_corridas, tiradas_por_corrida, numero_elegido):
    todas_las_frec = []
    resultados_concat = []

    for _ in range(num_corridas):
        corrida = simular_tiradas(tiradas_por_corrida)
        resultados_concat.extend(corrida)
        frec = calcular_frecuencia_acumulada(corrida, numero_elegido)
        todas_las_frec.append(frec)

    frec_concat = calcular_frecuencia_acumulada(
        resultados_concat, numero_elegido)
    media_concat = calcular_media_acumulada(resultados_concat)
    varianza_concat = calcular_varianza_acumulada(resultados_concat)
    desvio_concat = calcular_desvio_acumulado(resultados_concat)

    return todas_las_frec, resultados_concat, frec_concat, media_concat, varianza_concat, desvio_concat
