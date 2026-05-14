
from motor import simular

FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89,
       144, 233, 377, 610, 987, 1597, 2584, 4181]


__all__ = [
    "estrategia_fibonacci",
    "estrategia_dAlembert",
    "estrategia_martingala",
    "estrategia_paroli",
]


# ACTUALIZADORES DE FUNCIÓN DE APUESTA PARA CADA ESTRATEGIA


def _fib_update(info_ronda: dict):
    """Avanza en la secuencia de Fibonacci al perder, retrocede 2 al ganar."""
    apuesta_ini = info_ronda["apuesta_ini"]
    gano = info_ronda["gano"]
    indice_fib = info_ronda["estado"]

    if gano:
        indice_fib = max(0, indice_fib - 2)
    else:
        indice_fib += 1
    return apuesta_ini * FIB[indice_fib], indice_fib


def _dalembert_update(info_ronda: dict):
    """Suma una unidad al perder, resta una unidad al ganar."""
    apuesta = info_ronda["apuesta"]
    gano = info_ronda["gano"]
    apuesta_ini = info_ronda["apuesta_ini"]

    if gano:
        return max(apuesta_ini, apuesta - apuesta_ini), None
    else:
        return apuesta + apuesta_ini, None


def _martingala_update(info_ronda: dict):
    """Duplica la apuesta al perder, reinicia al ganar."""
    apuesta = info_ronda["apuesta"]
    gano = info_ronda["gano"]
    apuesta_ini = info_ronda["apuesta_ini"]

    if gano:
        return apuesta_ini, None
    else:
        return apuesta * 2, None


def _paroli_update(info_ronda: dict):
    """Duplica al ganar (hasta 3 rachas), reinicia al perder."""
    apuesta = info_ronda["apuesta"]
    gano = info_ronda["gano"]
    apuesta_ini = info_ronda["apuesta_ini"]
    rachas = info_ronda["estado"]

    if gano:
        nueva = apuesta * 2
        rachas += 1
        if rachas == 3:
            nueva = apuesta_ini
            rachas = 0
        return nueva, rachas
    else:
        return apuesta_ini, 0


# ============
# ESTRATEGIAS
# ============

def estrategia_fibonacci(capital_ini: float, apuesta_ini: int, tiradas: int) -> dict:
    return simular(capital_ini, apuesta_ini, tiradas,
                   _fib_update, "Fibonacci", estado_ini=0)


def estrategia_dAlembert(capital_ini: float, apuesta_ini: int, tiradas: int) -> dict:
    return simular(capital_ini, apuesta_ini, tiradas,
                   _dalembert_update, "dAlembert")


def estrategia_martingala(capital_ini: float, apuesta_ini: int, tiradas: int) -> dict:
    return simular(capital_ini, apuesta_ini, tiradas,
                   _martingala_update, "Martingala")


def estrategia_paroli(capital_ini: float, apuesta_ini: int, tiradas: int) -> dict:
    return simular(capital_ini, apuesta_ini, tiradas,
                   _paroli_update, "Paroli", estado_ini=0)
