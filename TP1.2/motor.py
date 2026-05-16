
import random
from constantes import NRO_ROJOS


def simular(
    capital_ini: float,
    apuesta_ini: int,
    tiradas: int,
    actualizar_apuesta,
    nombre: str,
    estado_ini=None,
) -> dict:
    if capital_ini == float('inf'):
        capital = 0
    else:
        capital = capital_ini
    apuesta = apuesta_ini
    # var estado es solo para estrategias que necesitan un estado adicional (como Fibonacci o Paroli)
    estado = estado_ini
    historial_capital: list[float] = []
    historial_apuestas: list[int] = []
    historial_frecuencia: list[float] = []
    aciertos = 0
    bancarrota = False

    for _ in range(tiradas):
        historial_capital.append(capital)
        historial_apuestas.append(apuesta)

        if capital < apuesta and capital_ini != float('inf'):
            bancarrota = True
            break

        numero = random.randint(0, 36)
        gano = numero in NRO_ROJOS
        if gano:
            aciertos += 1
            capital += apuesta
        else:
            capital -= apuesta

        info_ronda = {
            "apuesta": apuesta,
            "gano": gano,
            "apuesta_ini": apuesta_ini,
            "estado": estado,
        }

        apuesta, estado = actualizar_apuesta(info_ronda)
        historial_frecuencia.append(aciertos / (len(historial_frecuencia) + 1))

    return {
        "nombre": nombre,
        "historial_capital": historial_capital,
        "historial_apuestas": historial_apuestas,
        "historial_frecuencia": historial_frecuencia,
        "capital_final": capital,
        "bancarrota": bancarrota,
    }
