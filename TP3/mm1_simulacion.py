"""
Simulacion de Cola M/M/1/K  (usando SimPy)
============================================
Modelo de cola con:
  - Llegadas Poisson (tasa lambda)
  - Servicio exponencial (tasa mu)
  - 1 servidor
  - Capacidad maxima K (incluye al que se esta atendiendo)

Si llega un cliente y ya hay K en el sistema, se rechaza (bloqueo).
"""

import os
import simpy
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================
# PARTE 1: SIMULACION CON SIMPY
# =============================================================

def simular(lam, mu, K, tiempo_total=10000, warmup=1000, semilla=None):
    """
    Simula la cola M/M/1/K usando SimPy.

    Parametros:
        lam          - tasa de llegadas
        mu           - tasa de servicio
        K            - capacidad maxima del sistema
        tiempo_total - cuanto tiempo simular
        warmup       - periodo de calentamiento (se descarta)
        semilla      - para reproducir resultados
    """

    if semilla is not None:
        random.seed(semilla)

    # Contadores (listas de 1 elemento para poder modificarlos desde funciones internas)
    clientes_en_sistema = [0]
    llegadas  = [0]
    bloqueos  = [0]
    salidas   = [0]

    # Listas para guardar los tiempos individuales medidos directamente
    tiempos_en_cola = []
    tiempos_en_sistema = []

    # Series temporales para graficos de convergencia (L y W en relacion al tiempo)
    serie_L = []
    serie_W = []
    serie_t = []

    # Acumuladores de area (para promedios ponderados por tiempo)
    acum_clientes = [0.0]
    acum_cola     = [0.0]
    acum_servidor = [0.0]
    tiempo_en_estado = [0.0] * (K + 2)

    ultimo_evento = [0.0]
    grabando      = [False]

    def actualizar(ahora):
        if not grabando[0]:
            return
        dt = ahora - ultimo_evento[0]
        if dt <= 0:
            return
        n = clientes_en_sistema[0]
        acum_clientes[0] += n * dt
        acum_cola[0]     += max(0, n - 1) * dt
        acum_servidor[0] += (1 if n > 0 else 0) * dt
        if n <= K:
            tiempo_en_estado[n] += dt

    def proceso_cliente(env, servidor):
        actualizar(env.now)
        tiempo_llegada = env.now  # momento de llegada del cliente

        if clientes_en_sistema[0] >= K:
            bloqueos[0] += 1
            ultimo_evento[0] = env.now
            return

        clientes_en_sistema[0] += 1
        llegadas[0] += 1
        ultimo_evento[0] = env.now

        with servidor.request() as turno:
            yield turno
            # El cliente sale de la cola y empieza su atencion
            if grabando[0]:
                tiempos_en_cola.append(env.now - tiempo_llegada)

            actualizar(env.now)
            ultimo_evento[0] = env.now
            yield env.timeout(random.expovariate(mu))

        # El cliente termina y sale del sistema
        actualizar(env.now)
        clientes_en_sistema[0] -= 1
        salidas[0] += 1
        ultimo_evento[0] = env.now
        
        if grabando[0]:
            tiempos_en_sistema.append(env.now - tiempo_llegada)

    def generador_llegadas(env, servidor):
        while True:
            yield env.timeout(random.expovariate(lam))
            env.process(proceso_cliente(env, servidor))

    def activar_grabacion(env):
        yield env.timeout(warmup)
        grabando[0]       = True
        acum_clientes[0]  = 0.0
        acum_cola[0]      = 0.0
        acum_servidor[0]  = 0.0
        for i in range(len(tiempo_en_estado)):
            tiempo_en_estado[i] = 0.0
        llegadas[0]  = 0
        bloqueos[0]  = 0
        salidas[0]   = 0
        tiempos_en_cola.clear()
        tiempos_en_sistema.clear()
        serie_L.clear()
        serie_W.clear()
        serie_t.clear()
        ultimo_evento[0] = env.now

    def monitor_convergencia(env):
        """Monitorea como L y W van cambiando a lo largo del tiempo de simulacion."""
        yield env.timeout(warmup + 100)  # espera warmup + intervalo inicial
        while True:
            duracion = env.now - warmup
            if duracion > 0:
                L_temp = acum_clientes[0] / duracion
                W_temp = np.mean(tiempos_en_sistema) if tiempos_en_sistema else 0.0
                serie_L.append(L_temp)
                serie_W.append(W_temp)
                serie_t.append(duracion)
            yield env.timeout(100)  # cada 100 unidades de tiempo guarda un punto

    # Armar y correr
    env = simpy.Environment()
    servidor = simpy.Resource(env, capacity=1)
    env.process(generador_llegadas(env, servidor))
    env.process(activar_grabacion(env))
    env.process(monitor_convergencia(env))
    env.run(until=tiempo_total)
    actualizar(tiempo_total)

    # Calcular metricas
    duracion = tiempo_total - warmup

    L           = acum_clientes[0] / duracion
    Lq          = acum_cola[0]     / duracion
    utilizacion = acum_servidor[0] / duracion
    Pn = [t / duracion for t in tiempo_en_estado]

    total_intentos = llegadas[0] + bloqueos[0]
    P_bloqueo = bloqueos[0] / total_intentos if total_intentos > 0 else 0.0

    # Calculo directo de promedios de tiempo usando la lista
    W  = np.mean(tiempos_en_sistema) if tiempos_en_sistema else 0.0
    Wq = np.mean(tiempos_en_cola) if tiempos_en_cola else 0.0

    return {
        'L': L, 'Lq': Lq, 'W': W, 'Wq': Wq,
        'utilizacion': utilizacion, 'P_bloqueo': P_bloqueo,
        'Pn': Pn, 'llegadas': llegadas[0],
        'bloqueos': bloqueos[0], 'salidas': salidas[0],
        'serie_L': serie_L, 'serie_W': serie_W, 'serie_t': serie_t,
        'tiempos_en_cola': tiempos_en_cola,
        'tiempos_en_sistema': tiempos_en_sistema,
    }


# =============================================================
# PARTE 2: MULTIPLES CORRIDAS Y EXPERIMENTO FACTORIAL
# =============================================================

def correr_varias_veces(lam, mu, K, n_corridas=10, tiempo_total=10000, warmup=1000):
    """
    Corre la simulacion varias veces con semillas distintas y promedia.
    """
    resultados = []
    for i in range(n_corridas):
        semilla = i * 26
        r = simular(lam, mu, K, tiempo_total, warmup, semilla)
        resultados.append(r)

    def promedio(metrica):
        return sum(r[metrica] for r in resultados) / n_corridas

    promedios = {
        'L':           promedio('L'),
        'Lq':          promedio('Lq'),
        'W':           promedio('W'),
        'Wq':          promedio('Wq'),
        'utilizacion': promedio('utilizacion'),
        'P_bloqueo':   promedio('P_bloqueo'),
    }

    return resultados, promedios


def experimento_completo(mu=1.0, valores_K=None, valores_rho=None,
                         n_corridas=10, tiempo_total=10000, warmup=1000):
    """
    Corre todos los K x rho del enunciado.
    K   = [0, 2, 5, 10, 50]
    rho = [0.25, 0.50, 0.75, 1.00, 1.25]
    """
    if valores_K is None:
        valores_K = [0, 2, 5, 10, 50]
    if valores_rho is None:
        valores_rho = [0.25, 0.50, 0.75, 1.00, 1.25]

    resultados = {}
    total = len(valores_K) * len(valores_rho)
    contador = 0

    for K in valores_K:
        for rho in valores_rho:
            lam = rho * mu
            contador += 1
            print(f"  [{contador}/{total}]  K={K:>3}   rho={rho:.2f}   lambda={lam:.3f}")

            corridas, promedios = correr_varias_veces(lam, mu, K, n_corridas, tiempo_total, warmup)
            resultados[(K, rho)] = {
                'corridas':  corridas,
                'sim':       promedios,
                'lam': lam, 'mu': mu, 'K': K, 'rho': rho,
            }
            # Dashboard por combinacion
            graficar_resultados_corrida(corridas[0], lam, mu, K, num_corrida=1)

    return resultados


# =============================================================
# PARTE 3: TABLA DE RESULTADOS
# =============================================================

def mostrar_tabla(resultados):
    """Imprime una tabla resumen de todos los experimentos."""

    print()
    print("=" * 95)
    print("  RESULTADOS DE SIMULACION — M/M/1/K")
    print("=" * 95)
    print(f"  {'K':>4}  {'rho':>5}  {'L':>7}  {'Lq':>7}  {'W':>7}  {'Wq':>7}  {'Util':>6}  {'P_bloq':>7}")
    print(f"  {'-'*90}")

    for (K, rho), exp in sorted(resultados.items()):
        s = exp['sim']
        print(
            f"  {K:>4}  {rho:>5.2f}"
            f"  {s['L']:>7.4f}  {s['Lq']:>7.4f}"
            f"  {s['W']:>7.4f}  {s['Wq']:>7.4f}"
            f"  {s['utilizacion']:>6.4f}  {s['P_bloqueo']:>7.4f}"
        )

    print("=" * 95)


# =============================================================
# PARTE 4: GRAFICOS
# =============================================================

# =============================================================
# PARTE 4: GRAFICOS
# =============================================================

def graficar_resultados_corrida(corrida, lam, mu, K, num_corrida=1):
    """
    Genera un dashboard de graficos para una unica corrida.
    Muestra:
      - Evolucion de L(t) y W(t) en el tiempo (convergencia)
      - Distribucion de tiempos individuales (histogramas de W y Wq)
      - Probabilidad de n clientes esperando en cola (Pn_cola)
      - Utilizacion del servidor (grafico de torta/barras)
    """
    porcentaje_arribo = (lam / mu) * 100


    # Creamos la figura de 2x4 para el dashboard
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle(
        f"Dashboard de Simulacion M/M/1/{K}\n"
        f"Parametros: lambda={lam:.2f}, mu={mu:.2f} Porcentaje Arribos: {porcentaje_arribo:.1f}% ",
        fontsize=14, fontweight='bold'
    )

    # --- 1. Promedio de clientes en el sistema L(t) ---
    ax = axes[0, 0]
    if corrida['serie_t']:
        ax.plot(corrida['serie_t'], corrida['serie_L'], color='steelblue', lw=1.5)
        ax.set_title("Clientes en sistema — L(t)")
        ax.set_xlabel("Tiempo de simulacion")
        ax.set_ylabel("Clientes promedio L")
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Sin datos de serie", ha='center', va='center')



    # --- 2. Tiempo promedio en sistema W(t) ---
    ax = axes[0, 1]
    if corrida['serie_t']:
        ax.plot(corrida['serie_t'], corrida['serie_W'], color='orange', lw=1.5)
        ax.set_title("Tiempo en sistema — W(t)")
        ax.set_xlabel("Tiempo de simulacion")
        ax.set_ylabel("Tiempo promedio W")
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Sin datos de serie", ha='center', va='center')

    # --- 3. Distribucion de tiempos en cola (Wq) ---
    ax = axes[0, 2]
    if corrida['tiempos_en_cola']:
        ax.hist(corrida['tiempos_en_cola'], bins=30, color='indianred', alpha=0.7, edgecolor='black', density=True)
        promedio_cola = np.mean(corrida['tiempos_en_cola'])
        ax.axvline(promedio_cola, color='darkred', linestyle='--', lw=2, label=f'Prom: {promedio_cola:.2f}')
        ax.set_title("Distribucion del Tiempo en Cola (Wq)")
        ax.set_xlabel("Tiempo esperando")
        ax.set_ylabel("Densidad de probabilidad")
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Sin datos en cola", ha='center', va='center')

    # --- 4. Aceptados vs Rechazados ---
    ax = axes[0, 3]
    aceptados = corrida['llegadas']
    rechazados = corrida['bloqueos']
    if aceptados + rechazados > 0:
        ax.pie([aceptados, rechazados], labels=[f"Aceptados\n({aceptados})", f"Rechazados\n({rechazados})"],
               colors=['mediumaquamarine', 'tomato'], autopct='%1.1f%%', startangle=90, explode=(0, 0.1) if rechazados > 0 else (0, 0))
    else:
        ax.text(0.5, 0.5, "Sin clientes", ha='center', va='center')
    ax.set_title("Aceptados vs Rechazados")

    # --- 5. Probabilidad de n clientes en cola ---
    ax = axes[1, 0]
    Pn_sistema = corrida['Pn']
    Pn_cola = [0.0] * (K + 1)
    if len(Pn_sistema) > 1:
        # P(cola = 0) = P(sistema = 0) + P(sistema = 1)
        Pn_cola[0] = Pn_sistema[0] + Pn_sistema[1]
        # P(cola = j) = P(sistema = j + 1)
        for j in range(1, K):
            if j + 1 < len(Pn_sistema):
                Pn_cola[j] = Pn_sistema[j + 1]

        n_mostrar = min(K + 1, 15)
        ax.bar(range(n_mostrar), Pn_cola[:n_mostrar], color='forestgreen', alpha=0.7, edgecolor='black')
        ax.set_title("Probabilidad de n Clientes en Cola")
        ax.set_xlabel("Clientes en cola (n)")
        ax.set_ylabel("Probabilidad")
        ax.set_xticks(range(n_mostrar))
        ax.grid(True, alpha=0.3, axis='y')
    else:
        ax.text(0.5, 0.5, "Sin datos de Pn", ha='center', va='center')

    # --- 6. Distribucion de tiempos en sistema (W) ---
    ax = axes[1, 1]
    if corrida['tiempos_en_sistema']:
        ax.hist(corrida['tiempos_en_sistema'], bins=30, color='purple', alpha=0.6, edgecolor='black', density=True)
        promedio_sist = np.mean(corrida['tiempos_en_sistema'])
        ax.axvline(promedio_sist, color='indigo', linestyle='--', lw=2, label=f'Prom: {promedio_sist:.2f}')
        ax.set_title("Distribucion del Tiempo en Sistema (W)")
        ax.set_xlabel("Tiempo en sistema")
        ax.set_ylabel("Densidad de probabilidad")
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Sin datos en sistema", ha='center', va='center')

    # --- 7. Utilizacion del servidor ---
    ax = axes[1, 2]
    util = corrida['utilizacion']
    ocio = 1.0 - util
    ax.pie([util, ocio], labels=[f"Ocupado\n({util:.1%})", f"Ocioso\n({ocio:.1%})"], 
           colors=['yellowgreen', 'lightgray'], startangle=90, explode=(0.05, 0))
    ax.set_title("Utilizacion del Servidor")

    # --- 8. (celda libre, se elimino el grafico duplicado de Pn de cola) ---
    axes[1, 3].axis('off')

    plt.tight_layout()
    # Usamos un nombre dinamico para el archivo basado en los parametros para que no se sobreescriban
    carpeta_destino = "imagenes/teoriaColas"
    os.makedirs(carpeta_destino, exist_ok=True)
    nombre_archivo = f"dashboard_K{K}_arribo{porcentaje_arribo:.0f}pct.png"
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
    plt.savefig(ruta_completa, dpi=120)
    print(f"\n  Dashboard de graficos guardado como: '{nombre_archivo}'")
    plt.show()
    plt.close()



# =============================================================
# PROGRAMA PRINCIPAL
# =============================================================

if __name__ == '__main__':

    print("\n=== SIMULADOR M/M/1/K (SimPy) ===")
    print("1. Experimento rapido (un solo caso)")
    print("2. Experimento completo (todos los K x rho)")
    print("3. Modo interactivo (ingresar parametros)")
    modo = input("\nElegir [1/2/3] (Enter = 1): ").strip() or "1"
    if modo == "3":
        # Modo interactivo
        print("\n--- Ingresar parametros ---")
        lam        = float(input("  lambda (tasa de llegadas) [0.8]:   ") or "0.8")
        mu         = float(input("  mu     (tasa de servicio)  [1.0]:   ") or "1.0")
        K          = int(  input("  K      (capacidad maxima)  [10]:    ") or "10")
        n_corridas = int(  input("  Numero de corridas         [10]:    ") or "10")

        print(f"\nSimulando M/M/1/{K}...")
        corridas, promedios = correr_varias_veces(lam, mu, K, n_corridas)

        print(f"\n{'Metrica':<25} {'Promedio':>10}")
        print("-" * 37)
        print(f"{'L  (clientes en sist.)':<25} {promedios['L']:>10.4f}")
        print(f"{'Lq (clientes en cola)':<25} {promedios['Lq']:>10.4f}")
        print(f"{'W  (tiempo en sist.)':<25} {promedios['W']:>10.4f}")
        print(f"{'Wq (tiempo en cola)':<25} {promedios['Wq']:>10.4f}")
        print(f"{'Utilizacion':<25} {promedios['utilizacion']:>10.4f}")
        print(f"{'P_bloqueo':<25} {promedios['P_bloqueo']:>10.6f}")

        # Graficamos los resultados usando la primera corrida
        graficar_resultados_corrida(corridas[0], lam, mu, K)

    elif modo == "2":
        # Experimento completo
        print(f"\nCorriendo todos los K x rho (25 combinaciones, 10 corridas c/u)...\n")
        resultados = experimento_completo()
        mostrar_tabla(resultados)

    else:
        # Experimento rapido variando tasas de arribo (25%, 50%, 75%, 100%, 125%)
        mu  = 1.0
        K   = 2
        tasas_arribo = [0.25, 0.50, 0.75, 1.00, 1.25]

        print(f"\nSimulando M/M/1/{K} variando las tasas de arribo (10 corridas por caso)...")
        
        for rho in tasas_arribo:
            lam = rho * mu
            print(f"\n--- Caso: Arribo al {rho*100:.0f}% de mu (lambda={lam:.2f}, mu={mu:.2f}) ---")
            corridas, promedios = correr_varias_veces(lam, mu, K)

            print(f"  {'Metrica':<25} {'Promedio':>10}")
            print(f"  {'-' * 37}")
            print(f"  {'L  (clientes en sist.)':<25} {promedios['L']:>10.4f}")
            print(f"  {'Lq (clientes en cola)':<25} {promedios['Lq']:>10.4f}")
            print(f"  {'W  (tiempo en sist.)':<25} {promedios['W']:>10.4f}")
            print(f"  {'Wq (tiempo en cola)':<25} {promedios['Wq']:>10.4f}")
            print(f"  {'Utilizacion':<25} {promedios['utilizacion']:>10.4f}")
            print(f"  {'P_bloqueo':<25} {promedios['P_bloqueo']:>10.6f}")

            # Guardamos el dashboard de graficos para este caso especifico usando la primera corrida
            graficar_resultados_corrida(corridas[0], lam, mu, K, num_corrida=1)

