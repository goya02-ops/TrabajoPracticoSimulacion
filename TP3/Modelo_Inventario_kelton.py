import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# Tamaño de demanda por cliente: distribucion discreta EXACTA del libro
# (Fig. 1.38, funcion demand()): valores {1,2,3,4} con probabilidades
# {1/6, 1/3, 1/3, 1/6}, via tabla de probabilidad acumulada.
_TAMANOS_DEMANDA      = [1, 2, 3, 4]
_PROBS_DEMANDA        = [1.0 / 6.0, 1.0 / 3.0, 1.0 / 3.0, 1.0 / 6.0]
_PROBS_ACUM_DEMANDA   = [1.0 / 6.0, 1.0 / 2.0, 5.0 / 6.0, 1.0]


def _tamano_demanda():
    """Genera un tamaño de demanda segun la tabla discreta del libro."""
    u = np.random.uniform(0.0, 1.0)
    for tam, p_acum in zip(_TAMANOS_DEMANDA, _PROBS_ACUM_DEMANDA):
        if u <= p_acum:
            return float(tam)
    return float(_TAMANOS_DEMANDA[-1])


def _media_tamano_demanda():
    return sum(t * p for t, p in zip(_TAMANOS_DEMANDA, _PROBS_DEMANDA))


def _varianza_tamano_demanda():
    mu = _media_tamano_demanda()
    return sum(p * (t - mu) ** 2 for t, p in zip(_TAMANOS_DEMANDA, _PROBS_DEMANDA))


# =============================================================
# PARTE 1: SIMULACION (fiel a Figs. 1.36-1.39 del libro)
# =============================================================

def simular_inventario(mean_interdemand, minlag, maxlag, T_revision, smalls, bigs,
                       K_ord, c, h, p, inv_inicial=60.0, num_dias=365.0, semilla=None):
    """
    Simula el modelo de inventario (s, S) de Law & Kelton, con la misma
    arquitectura de una sola orden pendiente a la vez del codigo original
    (Figs. 1.36-1.39): variables escalares amount/t_arribo, sin posicion
    de inventario separada. Valido porque T_revision=30 > maxlag=5 dias
    garantiza que cada orden llega antes de la revision siguiente.

    Parametros (misma notacion que el libro, en dias):
        mean_interdemand - tiempo medio entre clientes (dias)
        minlag, maxlag   - lead time, Uniforme(minlag, maxlag) dias
        T_revision       - cada cuantos dias se revisa el inventario
        smalls, bigs     - politica de reorden (s, S)
        K_ord            - costo fijo por orden (setup_cost)
        c                - costo incremental por unidad (incremental_cost)
        h                - costo de mantenimiento por unidad y por dia (holding_cost)
        p                - costo de faltante por unidad y por dia (shortage_cost, "pi")
        inv_inicial      - inventario inicial (initial_inv_level)
        num_dias         - duracion de la simulacion en dias
        semilla          - semilla aleatoria para reproducibilidad
    """
    if semilla is not None:
        np.random.seed(semilla)

    inv_level = float(inv_inicial)   # inventario fisico (puede ser negativo = faltante)
    amount    = 0.0                   # cantidad de la (unica) orden en transito
    t_arribo  = float('inf')          # sin orden pendiente al inicio (Fig. 1.35: init_model)

    t          = 0.0
    t_demanda  = np.random.exponential(mean_interdemand)
    t_revision = T_revision           # primera revision recien al cabo de un periodo (Fig. 1.35)
    t_ant      = 0.0

    costo_ord_acum = 0.0
    area_holding   = 0.0
    area_shortage  = 0.0

    hist_t  = [0.0]
    hist_inv = [inv_level]
    hist_co = [0.0]
    hist_cm = [0.0]
    hist_cf = [0.0]
    hist_ct = [0.0]

    while True:
        candidatos = [(t_arribo, 1), (t_demanda, 2), (num_dias, 3), (t_revision, 4)]
        t_sig, tipo_evento = min(candidatos, key=lambda ev: ev[0])
        dt = t_sig - t_ant
        t  = t_sig

        # Actualizar acumuladores de tiempo (Fig. 1.41: update_time_avg_stats)
        if inv_level < 0:
            area_shortage += -inv_level * dt
        elif inv_level > 0:
            area_holding += inv_level * dt

        if tipo_evento == 3:
            break   # fin de la simulacion

        elif tipo_evento == 1:
            # Llegada de la orden pendiente (Fig. 1.37: order_arrival)
            inv_level += amount
            t_arribo   = float('inf')   # ya no hay orden pendiente

        elif tipo_evento == 2:
            # Evento de demanda (Fig. 1.38: demand)
            demanda    = _tamano_demanda()
            inv_level -= demanda
            t_demanda  = t + np.random.exponential(mean_interdemand)

        else:
            # Evaluacion periodica de inventario (Fig. 1.39: evaluate)
            if inv_level < smalls:
                amount    = bigs - inv_level
                lead_time = np.random.uniform(minlag, maxlag)
                t_arribo  = t + lead_time
                costo_ord_acum += K_ord + c * amount
            t_revision = t + T_revision   # proxima revision (periodo fijo)

        t_ant = t

        hist_t.append(t)
        hist_inv.append(inv_level)
        hist_co.append(costo_ord_acum)
        hist_cm.append(h * area_holding)
        hist_cf.append(p * area_shortage)
        hist_ct.append(costo_ord_acum + h * area_holding + p * area_shortage)

    costo_mant  = h * area_holding
    costo_falt  = p * area_shortage
    costo_total = costo_ord_acum + costo_mant + costo_falt

    return {
        'costo_orden':         costo_ord_acum,
        'costo_mantenimiento': costo_mant,
        'costo_faltante':      costo_falt,
        'costo_total':         costo_total,
        'semilla':             semilla if semilla is not None else -1,
        'hist_t':  hist_t,  'hist_inv': hist_inv,
        'hist_co': hist_co, 'hist_cm':  hist_cm,
        'hist_cf': hist_cf, 'hist_ct':  hist_ct,
    }


# =============================================================
# PARTE 2: MULTIPLES CORRIDAS (agregado para cumplir el TP — el
# libro corre una unica simulacion larga por politica)
# =============================================================

def correr_varias_veces(mean_interdemand, minlag, maxlag, T_revision, smalls, bigs,
                        K_ord, c, h, p, inv_inicial=60.0, num_dias=365.0, n_corridas=10):
    """Ejecuta n_corridas independientes y devuelve la lista de corridas y los promedios."""
    corridas = []
    for i in range(n_corridas):
        sem = i * 23451 + 17
        r   = simular_inventario(mean_interdemand, minlag, maxlag, T_revision, smalls, bigs,
                                 K_ord, c, h, p, inv_inicial, num_dias, semilla=sem)
        corridas.append(r)

    def promedio(clave):
        return np.mean([c[clave] for c in corridas])

    def desvio(clave):
        return float(np.std([c[clave] for c in corridas], ddof=1))

    promedios = {
        'costo_orden':         promedio('costo_orden'),
        'costo_mantenimiento': promedio('costo_mantenimiento'),
        'costo_faltante':      promedio('costo_faltante'),
        'costo_total':         promedio('costo_total'),
        'std_orden':           desvio('costo_orden'),
        'std_mantenimiento':   desvio('costo_mantenimiento'),
        'std_faltante':        desvio('costo_faltante'),
        'std_total':           desvio('costo_total'),
    }

    return corridas, promedios


# =============================================================
# PARTE 3: VALORES TEORICOS (aproximados — el libro no calcula
# ninguno; este ejemplo existe porque no tiene solucion cerrada)
# =============================================================

def _densidad_normal(z):
    return math.exp(-z * z / 2.0) / math.sqrt(2.0 * math.pi)


def _acumulada_normal(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _perdida_normal_unitaria(z):
    """G(z) = phi(z) - z*(1 - Phi(z)), perdida esperada de una Normal(0,1) est."""
    return _densidad_normal(z) - z * (1.0 - _acumulada_normal(z))


def teoricos_inventario(mean_interdemand, minlag, maxlag, T_revision, smalls, bigs,
                        K_ord, c, h, p, num_dias=365.0, n_grid=500):
    """
    Estimacion teorica de un (T, s, S) con revision periodica, resolviendo
    NUMERICAMENTE la cadena de Markov del "nivel de inventario al momento
    de revisar" (bajo aproximacion fluida: demanda dentro de un ciclo se
    trata como un flujo determinista mas difusion gaussiana), en vez de
    una formula de un solo paso (protecion period + G(z)) que asume nivel
    de servicio alto. Esa formula de un solo paso se usa aca SOLO para
    recomendar un s razonable (s_teo_recomendado); para estimar el COSTO
    de una politica (s,S) dada, se resuelve el proceso completo:

      1. En cada revision, si el nivel y < smalls se pide bigs - y
         (llega bigs - D_lag despues del lead time medio, D_lag = demanda
         esperada durante ese lag); si y >= smalls no se pide. En ambos
         casos, el nivel en la SIGUIENTE revision es y menos la demanda de
         todo el ciclo (mas el pedido, si hubo). Esto define una cadena de
         Markov sobre una grilla de niveles; se resuelve su distribucion
         estacionaria pi(y) por iteracion de potencias.
      2. Con pi(y) se promedia, sobre todo el rango de y, el costo de
         Mantenimiento/Faltante de un ciclo tipico que arranca en y: la
         demanda dentro del ciclo se aproxima como un proceso con media
         determinista (recta, con el quiebre del lead time si hubo pedido)
         y varianza creciente en t (Poisson compuesta), integrando en cada
         instante el valor esperado de la parte positiva/negativa de una
         Normal(media(t), varianza(t)).

    Esto es sustancialmente mas preciso que la aproximacion de un solo
    paso cuando el nivel de servicio es bajo (faltante frecuente, no un
    evento raro de cola) — que es exactamente el caso de estas politicas.
    Sigue siendo una aproximacion (demanda tratada como fluida/gaussiana,
    lead time fijo en su promedio): no hay forma cerrada exacta.
    """
    lam       = 1.0 / mean_interdemand
    lag_medio = (minlag + maxlag) / 2.0
    mu_x      = _media_tamano_demanda()
    var_x     = _varianza_tamano_demanda()

    # --- Recomendacion de s (formula clasica de periodo de proteccion) ---
    pp_rec    = T_revision + lag_medio
    mu_pp_rec = lam * pp_rec * mu_x
    sigma_pp_rec = math.sqrt(lam * pp_rec * (var_x + mu_x ** 2))
    s_teo_recomendado = mu_pp_rec + 1.64 * sigma_pp_rec

    # --- Demanda por ciclo completo (T_revision) y durante el lead time ---
    mu_D    = lam * mu_x * T_revision
    var_D   = lam * T_revision * (var_x + mu_x ** 2)
    sigma_D = math.sqrt(var_D)
    D_lag   = lam * mu_x * lag_medio

    # --- Grilla de niveles "al momento de revisar" y cadena de Markov ---
    ancho  = max(8.0 * sigma_D, 50.0)
    ys     = np.linspace(smalls - ancho, bigs + ancho, n_grid)

    def _pesos_normal(centro):
        z = (ys - centro) / sigma_D
        w = np.exp(-0.5 * z ** 2)
        return w / w.sum()

    fila_pedido = _pesos_normal(bigs - mu_D)   # si se pide, el ciclo siempre "resetea" igual
    K = np.empty((n_grid, n_grid))
    for i, y in enumerate(ys):
        K[i, :] = fila_pedido if y < smalls else _pesos_normal(y - mu_D)

    pi = np.full(n_grid, 1.0 / n_grid)
    for _ in range(1000):
        pi_new = pi @ K
        pi_new /= pi_new.sum()
        if np.max(np.abs(pi_new - pi)) < 1e-12:
            pi = pi_new
            break
        pi = pi_new

    # --- Costo esperado de un ciclo que arranca en nivel y (con difusion) ---
    n_pasos = 60
    ts = np.linspace(0.0, T_revision, n_pasos + 1)
    dt = ts[1] - ts[0]

    def _valor_esperado_pos_neg(media, varianza):
        if varianza <= 1e-9:
            return max(media, 0.0), max(-media, 0.0)
        sigma = math.sqrt(varianza)
        z = media / sigma
        e_pos = media * _acumulada_normal(z) + sigma * _densidad_normal(z)
        return e_pos, e_pos - media

    def _integral_ciclo(y, es_pedido):
        ip = ineg = t_falt = 0.0
        for i, t in enumerate(ts):
            var_t = lam * t * (var_x + mu_x ** 2)
            if es_pedido and t > lag_medio:
                media_t = (bigs - D_lag) - lam * mu_x * (t - lag_medio)
            else:
                media_t = y - lam * mu_x * t
            e_pos, e_neg = _valor_esperado_pos_neg(media_t, var_t)
            prob_falt = 1.0 - _acumulada_normal(media_t / math.sqrt(var_t)) if var_t > 1e-9 else float(media_t < 0)
            peso = 0.5 if (i == 0 or i == n_pasos) else 1.0
            ip     += peso * e_pos
            ineg   += peso * e_neg
            t_falt += peso * prob_falt
        return ip * dt, ineg * dt, t_falt * dt

    ip_esp, ineg_esp, tfalt_esp, costo_ord_ciclo = 0.0, 0.0, 0.0, 0.0
    for y, w in zip(ys, pi):
        if w <= 0.0:
            continue
        es_pedido = y < smalls
        ip, ineg, tfalt = _integral_ciclo(y, es_pedido)
        ip_esp    += w * ip
        ineg_esp  += w * ineg
        tfalt_esp += w * tfalt
        if es_pedido:
            costo_ord_ciclo += w * (K_ord + c * (bigs - y))

    num_ciclos      = num_dias / T_revision
    costo_orden_teo = num_ciclos * costo_ord_ciclo
    costo_mant_teo  = h * num_ciclos * ip_esp
    costo_falt_teo  = p * num_ciclos * ineg_esp
    costo_total_teo = costo_orden_teo + costo_mant_teo + costo_falt_teo

    prob_pedido   = float(np.sum(pi[ys < smalls]))
    # "Fill rate" aproximado como 1 - fraccion de tiempo esperada en
    # faltante (P(nivel<0) integrada en el ciclo) — no es un fill rate de
    # unidades exacto (el modelo trata la demanda como flujo continuo, no
    # unidad por unidad), pero es coherente con el resto de los costos.
    fill_rate_teo = max(0.0, 1.0 - tfalt_esp / T_revision)

    return {
        's_teo_recomendado':   s_teo_recomendado,
        'costo_orden':         costo_orden_teo,
        'costo_mantenimiento': costo_mant_teo,
        'costo_faltante':      costo_falt_teo,
        'costo_total':         costo_total_teo,
        'fill_rate':           fill_rate_teo,
        'prob_pedido':         prob_pedido,
    }


# =============================================================
# PARTE 4: TABLA DE RESULTADOS
# =============================================================

def mostrar_tabla_inventario(mean_interdemand, minlag, maxlag, T_revision, smalls, bigs,
                             K_ord, c, h, p, n_corridas, promedios, num_dias=365.0):
    """
    Imprime una tabla comparando Python (simulacion), Teorico (aproximado) y
    una columna en blanco para completar a mano con los resultados de AnyLogic.
    """
    teo   = teoricos_inventario(mean_interdemand, minlag, maxlag, T_revision, smalls, bigs,
                                K_ord, c, h, p, num_dias)
    ct    = promedios['costo_total']
    ct_s  = promedios['std_total']
    ic_lo = ct - 1.96 * ct_s / np.sqrt(n_corridas)
    ic_hi = ct + 1.96 * ct_s / np.sqrt(n_corridas)

    filas_costos = [
        ("Costo de Orden",      promedios['costo_orden'],         teo['costo_orden']),
        ("Costo Mantenimiento", promedios['costo_mantenimiento'], teo['costo_mantenimiento']),
        ("Costo de Faltante",   promedios['costo_faltante'],      teo['costo_faltante']),
        ("Costo TOTAL",         promedios['costo_total'],         teo['costo_total']),
    ]

    print(f"\n{'='*78}")
    print(f"  INVENTARIO (s,S) — MODELO LAW & KELTON — smalls={smalls}, bigs={bigs}")
    print(f"{'='*78}")
    print(f"  mean_interdemand={mean_interdemand}d  lag~U({minlag},{maxlag})d  T_revision={T_revision}d  "
          f"K={K_ord}  i={c}  h={h:.4f}  pi={p:.4f}  num_dias={num_dias}")
    print(f"  Punto de reorden recomendado (~95% servicio, periodo proteccion): s_teo = {teo['s_teo_recomendado']:.1f} und")
    print(f"{'='*78}")
    print(f"  {'Medida':<24} {'Python (sim)':>14} {'Teorico (aprox.)':>18} {'AnyLogic':>14}")
    print(f"  {'-'*74}")
    for nombre, val_py, val_teo in filas_costos:
        print(f"  {nombre:<24} {val_py:>14.2f} {val_teo:>18.2f} {'':>14}")
    print(f"  {'-'*74}")
    print(f"  {'Fill Rate':<24} {'':>14} {teo['fill_rate']:>18.4f} {'':>14}")
    print(f"  {'-'*74}")
    print(f"  {'IC 95% Costo Total (Python)':<45} [{ic_lo:.1f}, {ic_hi:.1f}]")
    print(f"{'='*78}")

    return teo


# =============================================================
# PARTE 5: GRAFICOS
# =============================================================

def _muestreo_diario(hist_t, hist_inv, num_dias):
    """Resamplea una trayectoria (escalonada) a una grilla diaria 0..num_dias-1,
    tomando el valor vigente en cada dia (igual que root.regInv[i] en AnyLogic)."""
    hist_t   = np.asarray(hist_t)
    hist_inv = np.asarray(hist_inv)
    dias = np.arange(0, int(num_dias))
    idx  = np.searchsorted(hist_t, dias, side='right') - 1
    idx  = np.clip(idx, 0, len(hist_inv) - 1)
    return hist_inv[idx]


def _promedio_diario_inventario(corridas, num_dias):
    """Promedio dia a dia del nivel de inventario a traves de todas las corridas
    (misma metodologia que dsPromedioInv de AnyLogic: sumInv[i]/n_corridas)."""
    muestras = [_muestreo_diario(r['hist_t'], r['hist_inv'], num_dias) for r in corridas]
    return np.mean(muestras, axis=0)


def graficar_costos(corridas, promedios, smalls, bigs, teoricos=None, save_path=None, num_dias=365.0):
    """Dashboard 2x2: inventario en el tiempo, costos acumulados, barras y distribucion."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(f"Dashboard Modelo de Inventario (s={smalls}, S={bigs})",
                 fontsize=14, fontweight='bold')

    corr0 = corridas[0]

    dias_grid    = np.arange(0, int(num_dias))
    inv_promedio = _promedio_diario_inventario(corridas, num_dias)

    ax = axes[0, 0]
    ax.plot(dias_grid, inv_promedio, linewidth=2.0, color='darkgreen',
            label=f'Promedio ({len(corridas)} corridas)')
    ax.axhline(y=smalls, color='blue',   linestyle='--', alpha=0.7, label=f's={smalls}')
    ax.axhline(y=bigs,   color='purple', linestyle=':',  alpha=0.7, label=f'S={bigs}')
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlabel('Tiempo (dias)')
    ax.set_ylabel('Nivel de inventario')
    ax.set_title('Evolucion del Nivel de Inventario')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    t = corr0['hist_t']
    ax.plot(t, corr0['hist_co'], label='Costo Orden',    ds='steps-post')
    ax.plot(t, corr0['hist_cm'], label='Costo Mant.',    ds='steps-post')
    ax.plot(t, corr0['hist_cf'], label='Costo Faltante', ds='steps-post')
    ax.plot(t, corr0['hist_ct'], label='Costo Total',    color='black', linewidth=2, ds='steps-post')
    ax.set_xlabel('Tiempo (dias)')
    ax.set_ylabel('Costo Acumulado ($)')
    ax.set_title('Evolucion de Costos Acumulados')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    categorias = ['Orden', 'Mantenimiento', 'Faltante', 'Total']
    valores    = [promedios['costo_orden'], promedios['costo_mantenimiento'],
                  promedios['costo_faltante'], promedios['costo_total']]
    errores    = [promedios['std_orden'], promedios['std_mantenimiento'],
                  promedios['std_faltante'], promedios['std_total']]
    colores    = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
    ax.bar(categorias, valores, yerr=errores, capsize=5, color=colores, alpha=0.8)
    if teoricos:
        ax.axhline(y=teoricos['costo_total'], color='black', linestyle='--',
                   alpha=0.7, label=f"Teorico Total=${teoricos['costo_total']:.0f}")
        ax.legend(fontsize=9)
    ax.set_ylabel('Costo ($)')
    ax.set_title('Costos Promediados (Todas las corridas)')
    ax.grid(True, axis='y', alpha=0.3)
    for i, v in enumerate(valores):
        ax.text(i, v + errores[i] + 0.05 * max(valores), f'${v:.0f}', ha='center', fontsize=9)

    ax = axes[1, 1]
    cts = [r['costo_total'] for r in corridas]
    ax.hist(cts, bins=min(len(cts) // 2, 8), edgecolor='white', alpha=0.7, color='#9b59b6')
    ax.axvline(x=promedios['costo_total'], color='red', linestyle='--',
               label=f"Media=${promedios['costo_total']:.0f}")
    ax.set_xlabel('Costo Total ($)')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribucion del Costo Total')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=120)
    plt.show()
    plt.close()


def graficar_comparacion_runs(corridas, smalls, bigs, save_path=None):
    """Barras agrupadas con los costos de cada corrida individual."""
    fig, ax = plt.subplots(figsize=(10, 6))
    xs = np.arange(1, len(corridas) + 1)

    ax.bar(xs - 0.25, [r['costo_orden']         for r in corridas], 0.2,
           label='Orden',         color='#3498db', alpha=0.8)
    ax.bar(xs,        [r['costo_mantenimiento'] for r in corridas], 0.2,
           label='Mantenimiento', color='#2ecc71', alpha=0.8)
    ax.bar(xs + 0.25, [r['costo_faltante']      for r in corridas], 0.2,
           label='Faltante',      color='#e74c3c', alpha=0.8)

    ax.set_xlabel('Corrida')
    ax.set_ylabel('Costo ($)')
    ax.set_title(f'Desglose de costos por corrida — Inventario Kelton (s={smalls}, S={bigs})')
    ax.set_xticks(xs)
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=120)
    plt.show()
    plt.close()


# =============================================================
# PROGRAMA PRINCIPAL
# =============================================================

# Fijos (no se piden por linea de comandos): numero de corridas.
N_CORRIDAS  = 10

# Politicas (nombre, s, S) que se comparan en cada ejecucion.
# Recalibradas para T_revision=30 dias (revision mensual): con
# lambda=10 clientes/dia, el periodo de proteccion (~33.5 dias) acumula
# ~837 unidades de demanda esperada, por eso s,S son de este orden.
# Cada experimento tiene UN costo claramente dominante (~70% del total),
# sin que ese costo acapare el 100% (el otro queda como secundario, no
# catastrofico como s=50/150 con T_revision=30, que daba ~99% de faltante):
# Exp 1 (Conservadora, s=600,S=1350): domina Mantenimiento (~71%), Faltante
#   secundario (~25%).
# Exp 2 (Ajustada/JIT,  s=350,S=1100): domina Faltante (~70%), Mantenimiento
#   secundario (~28%).
EXPERIMENTOS_S_S = [("conservadora", 600, 1350), ("ajustada", 350, 1100)]


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Simulador de Inventario (s,S) — Modelo de Law & Kelton (en dias)')
    parser.add_argument('--mean_interdemand', type=float, default=0.1,  help='Tiempo medio entre clientes (dias)')
    parser.add_argument('--minlag',      type=float, default=2.0,  help='Lead time minimo (dias)')
    parser.add_argument('--maxlag',      type=float, default=5.0,  help='Lead time maximo (dias)')
    parser.add_argument('--T_revision',  type=float, default=30.0,  help='Cada cuantos dias se revisa el inventario')
    parser.add_argument('--K_ord',       type=float, default=100.0,  help='Costo fijo por orden (setup)')
    parser.add_argument('--c',           type=float, default=3.0,   help='Costo incremental por unidad')
    parser.add_argument('--h',           type=float, default=2.0,  help='Costo de mantenimiento ($/und/dia)')
    parser.add_argument('--p',           type=float, default=50.0, help='Costo de faltante ($/und/dia)')
    parser.add_argument('--num_dias',    type=float, default=365.0, help='Duracion de la simulacion (dias)')
    args = parser.parse_args()

    for nombre, s, S in EXPERIMENTOS_S_S:
        print(f"\nSimulacion Inventario Kelton — {nombre} (s={s}, S={S})")
        print(f"  mean_interdemand={args.mean_interdemand}d  lag~U({args.minlag},{args.maxlag})d  "
              f"T_revision={args.T_revision}d  K={args.K_ord}  i={args.c}  h={args.h:.4f}  pi={args.p:.4f}  "
              f"num_dias={args.num_dias}")

        corridas, promedios = correr_varias_veces(
            args.mean_interdemand, args.minlag, args.maxlag, args.T_revision, s, S,
            args.K_ord, args.c, args.h, args.p,
            inv_inicial=S, num_dias=args.num_dias, n_corridas=N_CORRIDAS
        )
        teo = mostrar_tabla_inventario(
            args.mean_interdemand, args.minlag, args.maxlag, args.T_revision, s, S,
            args.K_ord, args.c, args.h, args.p, N_CORRIDAS, promedios, args.num_dias
        )

        carpeta_destino = "imagenes/inventario_kelton"
        path_costos = os.path.join(carpeta_destino, f"dashboard_{nombre}.png")
        path_runs   = os.path.join(carpeta_destino, f"por_corrida_{nombre}.png")
        graficar_costos(corridas, promedios, s, S, teoricos=teo, save_path=path_costos, num_dias=args.num_dias)
        graficar_comparacion_runs(corridas, s, S, save_path=path_runs)
        print(f"Graficos guardados en la carpeta '{carpeta_destino}'")


if __name__ == '__main__':
    main()
