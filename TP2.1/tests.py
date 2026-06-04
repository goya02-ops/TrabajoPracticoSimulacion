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


def test_monobit(numeros, alfa=0.01):
    n = len(numeros)

    # Convertir los números a bits: 1 si >= 0.5, -1 si < 0.5
    bits = [1 if num >= 0.5 else -1 for num in numeros]

    # Suma de los bits (+1 y -1)
    S_n = sum(bits)

    # Estadístico de prueba: |S_n| / sqrt(n)
    s_obs = abs(S_n) / math.sqrt(n)

    # P-valor usando la función complementaria del error
    p_valor = math.erfc(s_obs / math.sqrt(2))

    pasa_test = p_valor >= alfa

    print("--- PRUEBA MONOBIT (Frecuencia) ---")
    print(f"N: {n}")
    print(f"Suma S_n: {S_n}")
    print(f"Estadístico s_obs: {s_obs:.4f}")
    print(f"P-valor: {p_valor:.4f}")

    if pasa_test:
        print(
            "RESULTADO: APROBADO (No se rechaza H0 - La cantidad de 0s y 1s es aproximadamente igual)")
    else:
        print(
            "RESULTADO: RECHAZADO (Se rechaza H0 - La cantidad de 0s y 1s NO es aproximadamente igual)")

    return pasa_test, s_obs, p_valor


def test_sumas_acumuladas(numeros, alfa=0.01):
    n = len(numeros)

    # Convertir los números a bits: 1 si >= 0.5, -1 si < 0.5
    bits = [1 if num >= 0.5 else -1 for num in numeros]

    # Calcular las sumas parciales acumuladas (random walk)
    sumas_parciales = []
    acumulado = 0
    for b in bits:
        acumulado += b
        sumas_parciales.append(acumulado)

    # El estadístico z es el máximo valor absoluto de las sumas parciales
    z = max(abs(s) for s in sumas_parciales)

    # P-valor: aproximación mediante la distribución normal estándar
    raiz_n = math.sqrt(n)
    suma_inf = 0
    for k in range(int((-raiz_n / z + 1) / 4), int((raiz_n / z - 1) / 4) + 1):
        suma_inf += math.erfc((4 * k + 1) * z / raiz_n) - math.erfc((4 * k + 3) * z / raiz_n)
    p_valor = 1 - suma_inf

    pasa_test = p_valor >= alfa

    print("--- PRUEBA DE SUMAS ACUMULADAS ---")
    print(f"N: {n}")
    print(f"Estadístico z (máx. suma acumulada): {z}")
    print(f"P-valor: {p_valor:.4f}")

    if pasa_test:
        print(
            "RESULTADO: APROBADO (No se rechaza H0 - Las sumas acumuladas son consistentes con la aleatoriedad)")
    else:
        print(
            "RESULTADO: RECHAZADO (Se rechaza H0 - Las sumas acumuladas NO son consistentes con la aleatoriedad)")

    return pasa_test, z, p_valor
