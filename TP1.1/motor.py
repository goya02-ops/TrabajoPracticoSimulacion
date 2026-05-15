import random

from calculos import (
    frecuencia_del_numero,
    todos_los_estadisticos,
    media_final,
)
from CONSTANTES import NUMERO_RULETA


def generar_numeros_ruleta(cantidad):
    """Genera números aleatorios de ruleta (0-36)."""
    return [random.choice(NUMERO_RULETA) for _ in range(cantidad)]


def simular_una_corrida(tiradas, numero_elegido):
    """Ejecuta una corrida y calcula frecuencia del número."""
    numeros = generar_numeros_ruleta(tiradas)
    frecuencia = frecuencia_del_numero(numeros, numero_elegido)
    return {
        'numeros': numeros,
        'frecuencia': frecuencia,
    }


def repetir_corridas(num_corridas, tiradas_por_corrida, numero_elegido):
    """Ejecuta múltiples corridas y concatena resultados."""
    todas_frec = []
    resultados_concat = []
    todas_las_medias = []

    for _ in range(num_corridas):
        corrida = simular_una_corrida(tiradas_por_corrida, numero_elegido)
        todas_frec.append(corrida['frecuencia'])
        resultados_concat.extend(corrida['numeros'])
        # Para Teorema Central del Límite: obtener la media de cada corrida individual
        media_corrida = media_final(corrida['numeros'])
        todas_las_medias.append(media_corrida)

    return {
        'todas_frec': todas_frec,
        'resultados_concat': resultados_concat,
        'todas_las_medias': todas_las_medias,
    }


def calcular_todos_los_estadisticos(resultados_concat, numero_elegido):
    """Calcula todos los estadísticos en una pasada.
    
    Para Ley de los Grandes Números: estadísticos acumulados de todas las corridas.
    """
    calculos = todos_los_estadisticos(resultados_concat, numero_elegido)

    return {
        'frec_concat': calculos['frecuencia'],
        'media_concat': calculos['media'],
        'varianza_concat': calculos['varianza'],
        'desvio_concat': calculos['desvio'],
    }


def iniciar_experimento(num_corridas, tiradas_por_corrida, numero_elegido):
    """Orquestador principal: ejecuta corridas, concatena resultados y calcula estadísticos."""
    resultados_corridas = repetir_corridas(
        num_corridas, tiradas_por_corrida, numero_elegido)

    estadisticos = calcular_todos_los_estadisticos(
        resultados_corridas['resultados_concat'], numero_elegido)

    return {
        'todas_frec': resultados_corridas['todas_frec'],
        'resultados_concat': resultados_corridas['resultados_concat'],
        'todas_las_medias': resultados_corridas['todas_las_medias'],
        'frec_concat': estadisticos['frec_concat'],
        'media_concat': estadisticos['media_concat'],
        'varianza_concat': estadisticos['varianza_concat'],
        'desvio_concat': estadisticos['desvio_concat'],
    }
