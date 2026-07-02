"""
Simulador de Inventario (s, S) — Revision continua
===================================================
Politica (s, S): cuando la posicion de inventario cae a s o menos,
se ordena hasta alcanzar el nivel S.

JUSTIFICACION DE PARAMETROS (base):
------------------------------------
  λ = 10 und/dia     Demanda diaria (Poisson) — articulo de volumen medio
  L = 3 dias         Plazo de entrega fijo — tipico en distribucion local
  K_ord = $50        Costo fijo por orden — administrativo + preparacion
  h = $1/und/dia     Costo de mantenimiento — ~30% anual sobre $100
  p = $10/und/dia    Costo de faltante — perdida de venta + penalizacion
  s = 40 und         Punto de reorden = λL + SS = 30 + 10 (z≈1.64)
  S = 72 und         Nivel maximo = s + EOQ donde EOQ ≈ √(2λK/h) ≈ 32
  T = 365 dias       Horizonte de simulacion (1 año)
  Warmup = 30 dias   Periodo de calentamiento

FORMULAS DE REFERENCIA (EOQ deterministico):
  EOQ = √(2·λ·K_ord / h)
  Costo total anual = K_ord·(λ/Q) + h·(Q/2) + p·E[Faltante]
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import argparse

plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.size'] = 10


# =============================================================================
# 1. ESTRUCTURAS
# =============================================================================

@dataclass
class CorridaInventario:
    costo_orden: float
    costo_mantenimiento: float
    costo_faltante: float
    costo_total: float
    num_ordenes: int
    nivel_promedio: float
    faltante_promedio: float
    fill_rate: float
    semilla: int
    t_inv: List[float]
    inv_t: List[float]


@dataclass
class ExperimentoInventario:
    lam: float; L: float; s: int; S: int
    K_ord: float; h: float; p: float
    n_corridas: int
    co_m: float; co_s: float
    cm_m: float; cm_s: float
    cf_m: float; cf_s: float
    ct_m: float; ct_s: float
    num_ord_m: float
    fill_rate_m: float
    corridas: List[CorridaInventario]


# =============================================================================
# 2. SIMULACION
# =============================================================================

def simular_inventario(
    lam: float,          # tasa de demanda (unidades/dia)
    L: float,            # plazo de entrega (dias)
    s: int,              # punto de reorden
    S: int,              # nivel maximo
    K_ord: float,        # costo fijo por orden
    h: float,            # costo de mantenimiento (por und/dia)
    p: float,            # costo de faltante (por und/dia)
    tiempo_sim: float = 365.0,
    calentamiento: float = 30.0,
    semilla: Optional[int] = None
) -> CorridaInventario:
    if semilla is not None:
        np.random.seed(semilla)

    inv_nivel = float(S)     # inventario fisico (puede ser negativo)
    inv_pos = float(S)       # posicion de inventario (fisico + en transito)
    ordenes = []             # [(tiempo_entrega, cantidad)]
    t = 0.0
    t_dem = np.random.exponential(1.0 / lam)
    t_ent = float('inf')

    area_inv = 0.0          # integral de max(0, inv_nivel)
    area_falt = 0.0         # integral de max(0, -inv_nivel)
    n_ordenes = 0
    costo_ord_acum = 0.0
    t_ant = 0.0

    dem_atendidas = 0
    dem_total = 0
    grabando = False
    t_inicio = 0.0

    # Registro historico
    hist_t = [0.0]
    hist_inv = [inv_nivel]

    def prox_entrega():
        nonlocal t_ent
        t_ent = min((o[0] for o in ordenes), default=float('inf'))

    while t < tiempo_sim:
        if t_dem <= t_ent:
            dt = t_dem - t_ant
            t = t_dem

            if grabando:
                area_inv += max(0.0, inv_nivel) * dt
                area_falt += max(0.0, -inv_nivel) * dt

            dem_total += 1
            inv_nivel -= 1.0
            inv_pos -= 1.0
            if inv_nivel >= 0:
                dem_atendidas += 1

            if inv_pos <= s:
                q = S - inv_pos
                ordenes.append((t + L, q))
                inv_pos += q
                n_ordenes += 1
                costo_ord_acum += K_ord
                prox_entrega()

            t_dem = t + np.random.exponential(1.0 / lam)
        else:
            dt = t_ent - t_ant
            t = t_ent

            if grabando:
                area_inv += max(0.0, inv_nivel) * dt
                area_falt += max(0.0, -inv_nivel) * dt

            q_entregar = 0.0
            restantes = []
            for o in ordenes:
                if abs(o[0] - t) < 1e-9:
                    q_entregar += o[1]
                else:
                    restantes.append(o)
            ordenes = restantes
            inv_nivel += q_entregar
            prox_entrega()

        t_ant = t
        hist_t.append(t)
        hist_inv.append(inv_nivel)

        if not grabando and t >= calentamiento:
            grabando = True
            area_inv = 0.0
            area_falt = 0.0
            n_ordenes = 0
            costo_ord_acum = 0.0
            dem_atendidas = 0
            dem_total = 0
            t_inicio = t

    dur = tiempo_sim - calentamiento
    if dur <= 0:
        dur = tiempo_sim

    costo_mant = h * area_inv
    costo_falt = p * area_falt
    costo_total = costo_ord_acum + costo_mant + costo_falt
    nivel_prom = area_inv / dur
    falt_prom = area_falt / dur
    fill_rate = dem_atendidas / dem_total if dem_total > 0 else 1.0

    return CorridaInventario(
        costo_orden=costo_ord_acum,
        costo_mantenimiento=costo_mant,
        costo_faltante=costo_falt,
        costo_total=costo_total,
        num_ordenes=n_ordenes,
        nivel_promedio=nivel_prom,
        faltante_promedio=falt_prom,
        fill_rate=fill_rate,
        semilla=semilla if semilla else -1,
        t_inv=hist_t, inv_t=hist_inv
    )


# =============================================================================
# 3. EXPERIMENTO
# =============================================================================

def experimento_inventario(
    lam=10.0, L=3.0, s=40, S=72,
    K_ord=50.0, h=1.0, p=10.0,
    n_corridas=10, tiempo_sim=365.0, calentamiento=30.0
) -> ExperimentoInventario:
    corridas = []
    for i in range(n_corridas):
        sem = i * 23451 + 17
        r = simular_inventario(lam, L, s, S, K_ord, h, p,
                                tiempo_sim, calentamiento, semilla=sem)
        corridas.append(r)

    cov = [c.costo_orden for c in corridas]
    cmv = [c.costo_mantenimiento for c in corridas]
    cfv = [c.costo_faltante for c in corridas]
    ctv = [c.costo_total for c in corridas]
    nov = [c.num_ordenes for c in corridas]
    frv = [c.fill_rate for c in corridas]

    return ExperimentoInventario(
        lam=lam, L=L, s=s, S=S, K_ord=K_ord, h=h, p=p,
        n_corridas=n_corridas,
        co_m=float(np.mean(cov)), co_s=float(np.std(cov, ddof=1)),
        cm_m=float(np.mean(cmv)), cm_s=float(np.std(cmv, ddof=1)),
        cf_m=float(np.mean(cfv)), cf_s=float(np.std(cfv, ddof=1)),
        ct_m=float(np.mean(ctv)), ct_s=float(np.std(ctv, ddof=1)),
        num_ord_m=float(np.mean(nov)),
        fill_rate_m=float(np.mean(frv)),
        corridas=corridas
    )


# =============================================================================
# 4. REPORTE
# =============================================================================

def mostrar_tabla_inventario(exp: ExperimentoInventario):
    EOQ = np.sqrt(2 * exp.lam * exp.K_ord / exp.h)
    print(f"\n{'='*85}")
    print(f"EXPERIMENTO INVENTARIO (s,S) — s={exp.s}, S={exp.S}")
    print(f"{'='*85}")
    print(f"Parametros: λ={exp.lam}/dia  L={exp.L} dias  K_ord=${exp.K_ord}  h=${exp.h}/dia  p=${exp.p}/dia")
    print(f"Referencia: EOQ = {EOQ:.1f}  s_teo = {exp.lam*exp.L + 1.64*np.sqrt(exp.lam*exp.L):.1f}")
    print(f"{'='*85}")
    print(f"{'Medida':<30} {'Promedio':>12} {'Std Dev':>12}")
    print(f"{'-'*55}")
    print(f"{'Costo de Orden':<30} {exp.co_m:>12.2f} {exp.co_s:>12.2f}")
    print(f"{'Costo Mantenimiento':<30} {exp.cm_m:>12.2f} {exp.cm_s:>12.2f}")
    print(f"{'Costo de Faltante':<30} {exp.cf_m:>12.2f} {exp.cf_s:>12.2f}")
    print(f"{'Costo TOTAL':<30} {exp.ct_m:>12.2f} {exp.ct_s:>12.2f}")
    print(f"{'-'*55}")
    print(f"{'N° Ordenes':<30} {exp.num_ord_m:>12.1f}")
    print(f"{'Fill Rate':<30} {exp.fill_rate_m:>12.4f}")
    print(f"{'IC95% Costo Total':<30} [{exp.ct_m-1.96*exp.ct_s/np.sqrt(exp.n_corridas):.1f}, {exp.ct_m+1.96*exp.ct_s/np.sqrt(exp.n_corridas):.1f}]")
    print(f"{'='*85}")


# =============================================================================
# 5. GRAFICOS
# =============================================================================

def graficar_costos(exp: ExperimentoInventario, save_path: Optional[str] = None):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Barras de costos promedio
    categorias = ['Orden', 'Mantenimiento', 'Faltante', 'Total']
    valores = [exp.co_m, exp.cm_m, exp.cf_m, exp.ct_m]
    errores = [exp.co_s, exp.cm_s, exp.cf_s, exp.ct_s]
    colores = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
    axes[0].bar(categorias, valores, yerr=errores, capsize=5, color=colores, alpha=0.8)
    axes[0].set_ylabel('Costo ($)')
    axes[0].set_title('Costos promediados')
    axes[0].grid(True, axis='y', alpha=0.3)

    for i, v in enumerate(valores):
        axes[0].text(i, v + errores[i] + 0.05 * max(valores),
                     f'${v:.0f}', ha='center', fontsize=9)

    # Evolucion del inventario (primera corrida)
    corr0 = exp.corridas[0]
    t = corr0.t_inv
    inv = corr0.inv_t
    axes[1].plot(t, inv, linewidth=0.8, alpha=0.8)
    axes[1].axhline(y=exp.s, color='red', linestyle='--', alpha=0.5, label=f's={exp.s}')
    axes[1].axhline(y=exp.S, color='green', linestyle='--', alpha=0.5, label=f'S={exp.S}')
    axes[1].axhline(y=0, color='black', linewidth=0.5)
    axes[1].set_xlabel('Tiempo (dias)')
    axes[1].set_ylabel('Nivel de inventario')
    axes[1].set_title('Evolucion del inventario (1 corrida)')
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    # Distribucion del costo total entre corridas
    cts = [c.costo_total for c in exp.corridas]
    axes[2].hist(cts, bins=min(len(cts)//2, 8), edgecolor='white', alpha=0.7, color='#9b59b6')
    axes[2].axvline(x=exp.ct_m, color='red', linestyle='--', label=f'Media=${exp.ct_m:.0f}')
    axes[2].set_xlabel('Costo Total ($)')
    axes[2].set_ylabel('Frecuencia')
    axes[2].set_title('Distribucion del Costo Total')
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def graficar_comparacion_runs(exp: ExperimentoInventario, save_path: Optional[str] = None):
    fig, ax = plt.subplots(figsize=(10, 6))
    corridas = exp.corridas
    xs = np.arange(1, len(corridas) + 1)

    ax.bar(xs - 0.25, [c.costo_orden for c in corridas], 0.2,
           label='Orden', color='#3498db', alpha=0.8)
    ax.bar(xs, [c.costo_mantenimiento for c in corridas], 0.2,
           label='Mantenimiento', color='#2ecc71', alpha=0.8)
    ax.bar(xs + 0.25, [c.costo_faltante for c in corridas], 0.2,
           label='Faltante', color='#e74c3c', alpha=0.8)

    ax.set_xlabel('Corrida')
    ax.set_ylabel('Costo ($)')
    ax.set_title('Desglose de costos por corrida')
    ax.set_xticks(xs)
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


# =============================================================================
# 6. MAIN / CLI
# =============================================================================

def demo_inventario():
    print("\n>>> DEMO INVENTARIO (s,S) <<<\n")
    lam = float(input("  λ (demanda/dia, Poisson) [10]: ") or "10")
    L = float(input("  L (plazo entrega, dias) [3]: ") or "3")
    s = int(input("  s (punto reorden) [40]: ") or "40")
    S = int(input("  S (nivel maximo) [72]: ") or "72")
    Ko = float(input("  K_orden ($/orden) [50]: ") or "50")
    h = float(input("  h ($/und/dia) [1]: ") or "1")
    p = float(input("  p ($/und/dia) [10]: ") or "10")
    nc = int(input("  N° corridas [10]: ") or "10")
    ts = float(input("  Tiempo sim (dias) [365]: ") or "365")
    wu = float(input("  Calentamiento (dias) [30]: ") or "30")

    print("\nEjecutando simulacion...")
    exp = experimento_inventario(lam, L, s, S, Ko, h, p, nc, ts, wu)
    mostrar_tabla_inventario(exp)
    return exp


def main():
    parser = argparse.ArgumentParser(
        description='Simulador de Inventario (s,S) — Revision continua',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python inventario_simulacion.py --demo
  python inventario_simulacion.py --lam 10 --L 3 --s 40 --S 72
  python inventario_simulacion.py --s 30 --S 60 --corridas 20 --graficos
        """)
    parser.add_argument('--demo', action='store_true', help='Modo interactivo')
    parser.add_argument('--lam', type=float, default=10.0, help='Tasa de demanda')
    parser.add_argument('--L', type=float, default=3.0, help='Plazo de entrega')
    parser.add_argument('--s', type=int, default=40, help='Punto de reorden')
    parser.add_argument('--S', type=int, default=72, help='Nivel maximo')
    parser.add_argument('--K_ord', type=float, default=50.0, help='Costo por orden')
    parser.add_argument('--h', type=float, default=1.0, help='Costo mantenimiento')
    parser.add_argument('--p', type=float, default=10.0, help='Costo faltante')
    parser.add_argument('--corridas', type=int, default=10, help='Numero de corridas')
    parser.add_argument('--tiempo', type=float, default=365.0, help='Tiempo simulacion')
    parser.add_argument('--warmup', type=float, default=30.0, help='Calentamiento')
    parser.add_argument('--graficos', action='store_true', help='Generar graficos')
    parser.add_argument('--output', type=str, default=None, help='Prefijo graficos')

    args = parser.parse_args()

    if args.demo:
        demo_inventario()
        return

    print(f"\nSimulacion Inventario (s={args.s}, S={args.S})")
    print(f"  λ={args.lam}/dia  L={args.L}d  K_ord=${args.K_ord}  h=${args.h}/dia  p=${args.p}/dia")

    exp = experimento_inventario(
        args.lam, args.L, args.s, args.S,
        args.K_ord, args.h, args.p,
        args.corridas, args.tiempo, args.warmup
    )
    mostrar_tabla_inventario(exp)

    if args.graficos:
        pref = args.output or "inv_resultados"
        graficar_costos(exp, save_path=f"{pref}_costos.png")
        graficar_comparacion_runs(exp, save_path=f"{pref}_por_corrida.png")
        print(f"Graficos guardados como: {pref}_*.png")


if __name__ == '__main__':
    main()
