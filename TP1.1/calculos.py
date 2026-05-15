import statistics


# Calcula frecuencia relativa acumulada
def frecuencia_del_numero(resultados, numero_elegido):
    acumulada = []
    contador = 0
    for i, r in enumerate(resultados):
        if r == numero_elegido:
            contador += 1
        acumulada.append(contador / (i + 1))
    return acumulada


def todos_los_estadisticos(resultados, numero_elegido=None):
    """Calcula TODOS los estadísticos de todas las corridas concatenadas.
    NOTA: No usamos 'statistics' porque necesitamos valores acumulativos en cada punto.

    Ver explicación en README.md - sección "Notas técnicas".
    """
    frecuencia = [] if numero_elegido is not None else None
    media = []
    varianza = []

    suma = 0
    suma_cuadrados = 0
    contador = 0

    for i, r in enumerate(resultados):
        n = i + 1

        if numero_elegido is not None:
            # Frecuencia acumulada
            if r == numero_elegido:
                contador += 1
            frecuencia.append(contador / n)

        # Media acumulada
        suma += r
        media.append(suma / n)

        # Varianza acumulada
        suma_cuadrados += r ** 2
        if n >= 2:
            media_actual = suma / n
            var = (suma_cuadrados - n * media_actual ** 2) / (n - 1)
        else:
            var = 0
        varianza.append(var)

    # Desvío estándar acumulado
    desvio = [v ** 0.5 for v in varianza]

    resultado = {
        'media': media,
        'varianza': varianza,
        'desvio': desvio,
    }

    if numero_elegido is not None:
        resultado['frecuencia'] = frecuencia

    return resultado


def media_final(numeros):
    """Calcula la media final de una sola corrida."""
    return statistics.mean(numeros)
