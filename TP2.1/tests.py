import numpy as np
import math
from scipy.stats import chi2


def test_chi_cuadrado(numeros, num_celdas=10, alfa=0.01):

    n = len(numeros)

    esperado = n / num_celdas

    # observado: array de frecuencias observadas en cada celda, limites: array de los límites de las celdas
    observado, limites = np.histogram(
        numeros, bins=num_celdas, range=(0.0, 1.0))

    # Error acumulado entre lo observado y lo esperado
    chi_cuadrado_est = np.sum(((observado - esperado) ** 2) / esperado)

    grados_libertad = num_celdas - 1

    # Según la tala chi-cuadrado: necesitamos grados de libertad y la probabilidad de error para determinar un valor

    # Error máximo permitido para no rechazar H0.
    # En este caso, ppf nos devuelve el valor hasta dónde se acumula el 1-alfa% de la distribución chi-cuadrado con los grados de libertad dados.
    valor_critico = chi2.ppf(1 - alfa, grados_libertad)

    # En este caso, con cdf hacemos lo inverso: con los grados de libertad y el valor observado, nos devuelve la probabilidad acumulada hasta ese punto. Para obtener el p-valor, restamos a 1 esa probabilidad acumulada.
    p_valor = 1 - chi2.cdf(chi_cuadrado_est, grados_libertad)

    pasa_test = p_valor >= alfa

    print("--- PRUEBA CHI-CUADRADO ---")
    print(f"Celdas: {num_celdas} | N: {n}")
    print(f"Estadístico Chi-Cuadrado obtenido: {chi_cuadrado_est:.4f}")
    print(f"Valor Crítico teórico: {valor_critico:.4f}")
    print(f"P-valor: {p_valor:.4f}")

    if pasa_test:
        print(
            "RESULTADO: APROBADO (No se rechaza H0 - Los datos se ajustan a una Uniforme)")
    else:
        print("RESULTADO: RECHAZADO (Se rechaza H0 - Los datos NO son uniformes)")

    return pasa_test, chi_cuadrado_est


def test_rachas(numeros, alfa=0.01):
    n = len(numeros)
    # binarizar los números en 0 y 1
    bits = [1 if num >= 0.5 else 0 for num in numeros]

    # calcular proporción de 1s
    pi = sum(bits) / n

    tau = 2 / math.sqrt(n)
    if abs(pi - 0.5) >= tau:
        print("--- PRUEBA DE RACHAS ---")
        print(
            f"Fallo en Pre-test: La proporción de 1s es {pi:.4f}, fuera del rango permitido.")
        return False, 0.0

    v_obs = 1
    for k in range(n-1):
        if bits[k] != bits[k+1]:
            v_obs += 1

    numerador = abs(v_obs - 2 * n * pi * (1 - pi))
    denominador = 2 * math.sqrt(2 * n) * pi * (1 - pi)

    p_valor = math.erfc(numerador / denominador)

    pasa_test = p_valor >= alfa

    print("--- PRUEBA DE RACHAS ---")
    print(f"Proporcion de 1s (pi): {pi:.4f}")
    print(f"Rachas Observadas: {v_obs}")
    print(f"P-valor: {p_valor:.4f}")

    if pasa_test:
        print(
            "RESULTADO: APROBADO (No se rechaza H0 - Las rachas son consistentes con la aleatoriedad)")
    else:
        print(
            "RESULTADO: RECHAZADO (Se rechaza H0 - Las rachas NO son consistentes con la aleatoriedad)")

    return pasa_test, v_obs, p_valor
