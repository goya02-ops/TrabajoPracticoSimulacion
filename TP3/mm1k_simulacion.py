"""
Simulador M/M/1/K — Simulacion de eventos discretos
====================================================
Modelo de cola con llegadas Poisson, servicio exponencial,
capacidad finita K (incluye servidor).

MARCO TEORICO:
--------------
Para M/M/1/K con ρ = λ/μ:

  P0 = (1-ρ)/(1-ρ^(K+1))                 (ρ ≠ 1)
  Pn = ρ^n · P0                          n = 0,1,...,K

  L  = ρ/(1-ρ) - (K+1)·ρ^(K+1)/(1-ρ^(K+1))
  Lq = L - (1-P0)
  W  = L / λ_eff                          λ_eff = λ(1-PK)
  Wq = Lq / λ_eff
  ρ_eff = 1 - P0                          (utilizacion real)
  P_bloqueo = PK = ρ^K · P0

Para ρ = 1:
  P0 = 1/(K+1),  Pn = 1/(K+1),  L = K/2
  Lq = K(K-1)/(2(K+1))
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import argparse
import sys

plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.size'] = 10

# =============================================================================
# 1. TEORIA
# =============================================================================

def teoricas_mm1k(lam: float, mu: float, K: int) -> dict:
    rho = lam / mu
    if abs(rho - 1.0) < 1e-12:
        P0 = 1.0 / (K + 1)
        Pn = [P0] * (K + 1)
        L = K / 2.0
        Lq = K * (K - 1) / (2.0 * (K + 1))
        P_block = Pn[K]
    else:
        rhoK1 = rho ** (K + 1)
        P0 = (1.0 - rho) / (1.0 - rhoK1)
        Pn = [P0 * (rho ** n) for n in range(K + 1)]
        P_block = Pn[K]
        L = rho / (1.0 - rho) - (K + 1.0) * rhoK1 / (1.0 - rhoK1)
        Lq = L - (1.0 - P0)

    lambda_eff = lam * (1.0 - P_block)
    W = L / lambda_eff if lambda_eff > 0 else 0.0
    Wq = Lq / lambda_eff if lambda_eff > 0 else 0.0
    utilizacion = 1.0 - P0

    return {
        'rho': rho, 'L': L, 'Lq': Lq, 'W': W, 'Wq': Wq,
        'utilizacion': utilizacion, 'P0': P0, 'Pn': Pn,
        'P_block': P_block, 'lambda_eff': lambda_eff
    }


# =============================================================================
# 2. ESTRUCTURAS DE DATOS
# =============================================================================

@dataclass
class CorridaMM1K:
    L: float; Lq: float; W: float; Wq: float
    utilizacion: float; P_block: float
    Pn: List[float]
    num_llegadas: int; num_bloqueos: int; num_salidas: int
    semilla: int; tiempo_sim: float
    L_t: List[float] = field(default_factory=list)
    W_t: List[float] = field(default_factory=list)
    t_check: List[float] = field(default_factory=list)


@dataclass
class ExperimentoMM1K:
    lam: float; mu: float; K: int; rho: float; n_corridas: int
    L_m: float; L_s: float; Lq_m: float; Lq_s: float
    W_m: float; W_s: float; Wq_m: float; Wq_s: float
    util_m: float; util_s: float; pb_m: float; pb_s: float
    L_t: float; Lq_t: float; W_t: float; Wq_t: float
    util_t: float; pb_t: float
    err_L: float; err_Lq: float; err_W: float; err_Wq: float
    corridas: List[CorridaMM1K] = field(default_factory=list)


# =============================================================================
# 3. SIMULACION EVENTO DISCRETO
# =============================================================================

def simular_mm1k(
    lam: float, mu: float, K: int,
    tiempo_sim: float = 10000.0,
    calentamiento: float = 1000.0,
    semilla: Optional[int] = None,
    intervalo_ck: float = 100.0
) -> CorridaMM1K:
    if semilla is not None:
        np.random.seed(semilla)

    n = 0
    serv_oc = False
    t = 0.0
    t_lleg = np.random.exponential(1.0 / lam)
    t_sal = float('inf')

    area_n = 0.0; area_nq = 0.0; area_serv = 0.0
    t_ant = 0.0
    t_estado = [0.0] * (K + 2)

    n_lleg = 0; n_bloq = 0; n_sal = 0

    t_prox_ck = calentamiento + intervalo_ck
    ck_L = []; ck_W = []; ck_t = []
    grabando = False
    t_inicio = 0.0

    while t < tiempo_sim:
        if t_lleg <= t_sal:
            dt = t_lleg - t_ant; t = t_lleg
            if grabando:
                area_n += n * dt
                area_nq += max(0, n - 1) * dt
                area_serv += (1 if serv_oc else 0) * dt
                t_estado[min(n, K + 1)] += dt

            if n < K:
                n += 1; n_lleg += 1
                if not serv_oc:
                    serv_oc = True
                    t_sal = t + np.random.exponential(1.0 / mu)
                t_lleg = t + np.random.exponential(1.0 / lam)
            else:
                n_bloq += 1
                t_lleg = t + np.random.exponential(1.0 / lam)
        else:
            dt = t_sal - t_ant; t = t_sal
            if grabando:
                area_n += n * dt
                area_nq += max(0, n - 1) * dt
                area_serv += (1 if serv_oc else 0) * dt
                t_estado[min(n, K + 1)] += dt

            n -= 1; n_sal += 1
            if n > 0:
                t_sal = t + np.random.exponential(1.0 / mu)
            else:
                serv_oc = False; t_sal = float('inf')

        t_ant = t

        if not grabando and t >= calentamiento:
            grabando = True
            area_n = 0.0; area_nq = 0.0; area_serv = 0.0
            t_estado = [0.0] * (K + 2)
            n_lleg = 0; n_bloq = 0; n_sal = 0
            t_inicio = t; t_ant = t

        if grabando and t >= t_prox_ck:
            dur = t - t_inicio
            if dur > 0:
                la = area_n / dur
                le = n_lleg / dur
                ck_L.append(la)
                ck_W.append(la / le if le > 0 else 0)
                ck_t.append(dur)
            t_prox_ck += intervalo_ck

    dur_sim = tiempo_sim - calentamiento
    if dur_sim <= 1e-12:
        dur_sim = tiempo_sim

    L = area_n / dur_sim
    Lq = area_nq / dur_sim
    util = area_serv / dur_sim
    Pn_sim = [t / dur_sim for t in t_estado]

    total = n_lleg + n_bloq
    P_block = n_bloq / total if total > 0 else 0.0
    leff = n_lleg / dur_sim
    W = L / leff if leff > 0 else 0.0
    Wq = Lq / leff if leff > 0 else 0.0

    return CorridaMM1K(
        L=L, Lq=Lq, W=W, Wq=Wq, utilizacion=util,
        P_block=P_block, Pn=Pn_sim,
        num_llegadas=n_lleg, num_bloqueos=n_bloq,
        num_salidas=n_sal, semilla=semilla if semilla else -1,
        tiempo_sim=dur_sim,
        L_t=ck_L, W_t=ck_W, t_check=ck_t
    )


# =============================================================================
# 4. EXPERIMENTOS (MULTIPLES CORRIDAS)
# =============================================================================

def experimento_mm1k(
    lam: float, mu: float, K: int,
    n_corridas: int = 10,
    tiempo_sim: float = 10000.0,
    calentamiento: float = 1000.0
) -> ExperimentoMM1K:
    corridas = []
    for i in range(n_corridas):
        sem = i * 12347 + 41
        r = simular_mm1k(lam, mu, K, tiempo_sim, calentamiento, semilla=sem)
        corridas.append(r)

    teor = teoricas_mm1k(lam, mu, K)
    Lv = [c.L for c in corridas]
    Lqv = [c.Lq for c in corridas]
    Wv = [c.W for c in corridas]
    Wqv = [c.Wq for c in corridas]
    uv = [c.utilizacion for c in corridas]
    pv = [c.P_block for c in corridas]

    def ee(a, b):
        return abs(a - b) / b * 100 if abs(b) > 1e-12 else 0.0

    return ExperimentoMM1K(
        lam=lam, mu=mu, K=K, rho=lam/mu, n_corridas=n_corridas,
        L_m=float(np.mean(Lv)), L_s=float(np.std(Lv, ddof=1)),
        Lq_m=float(np.mean(Lqv)), Lq_s=float(np.std(Lqv, ddof=1)),
        W_m=float(np.mean(Wv)), W_s=float(np.std(Wv, ddof=1)),
        Wq_m=float(np.mean(Wqv)), Wq_s=float(np.std(Wqv, ddof=1)),
        util_m=float(np.mean(uv)), util_s=float(np.std(uv, ddof=1)),
        pb_m=float(np.mean(pv)), pb_s=float(np.std(pv, ddof=1)),
        L_t=teor['L'], Lq_t=teor['Lq'], W_t=teor['W'], Wq_t=teor['Wq'],
        util_t=teor['utilizacion'], pb_t=teor['P_block'],
        err_L=ee(np.mean(Lv), teor['L']),
        err_Lq=ee(np.mean(Lqv), teor['Lq']),
        err_W=ee(np.mean(Wv), teor['W']),
        err_Wq=ee(np.mean(Wqv), teor['Wq']),
        corridas=corridas
    )


def experimento_completo(
    mu: float = 1.0,
    valores_K: Optional[List[int]] = None,
    ratios_lambda: Optional[List[float]] = None,
    n_corridas: int = 10,
    tiempo_sim: float = 10000.0,
    calentamiento: float = 1000.0,
    verbose: bool = True
) -> dict:
    if valores_K is None:
        valores_K = [0, 2, 5, 10, 50]
    if ratios_lambda is None:
        ratios_lambda = [0.25, 0.50, 0.75, 1.00, 1.25]

    resultados = {}
    total = len(valores_K) * len(ratios_lambda)
    idx = 0
    for K in valores_K:
        for ratio in ratios_lambda:
            lam = ratio * mu
            idx += 1
            if verbose:
                print(f"  [{idx}/{total}] K={K:3d}  ρ={ratio:.2f}  λ={lam:.3f}")
            exp = experimento_mm1k(lam, mu, K, n_corridas, tiempo_sim, calentamiento)
            resultados[(K, ratio)] = exp
    return resultados


# =============================================================================
# 5. REPORTE / TABLA
# =============================================================================

def mostrar_tabla_experimento(exp: ExperimentoMM1K):
    print(f"\n{'='*85}")
    print(f"EXPERIMENTO: M/M/1/{exp.K}  |  λ={exp.lam:.3f}  μ={exp.mu:.3f}  ρ={exp.rho:.3f}")
    print(f"{'='*85}")
    print(f"{'Medida':<25} {'Simulacion':>12} {'Teorico':>12} {'Error %':>10}")
    print(f"{'-'*60}")
    print(f"{'L (clientes en sistema)':<25} {exp.L_m:>12.4f} {exp.L_t:>12.4f} {exp.err_L:>9.2f}%")
    print(f"{'Lq (clientes en cola)':<25} {exp.Lq_m:>12.4f} {exp.Lq_t:>12.4f} {exp.err_Lq:>9.2f}%")
    print(f"{'W (tiempo en sistema)':<25} {exp.W_m:>12.4f} {exp.W_t:>12.4f} {exp.err_W:>9.2f}%")
    print(f"{'Wq (tiempo en cola)':<25} {exp.Wq_m:>12.4f} {exp.Wq_t:>12.4f} {exp.err_Wq:>9.2f}%")
    print(f"{'Utilizacion':<25} {exp.util_m:>12.4f} {exp.util_t:>12.4f}")
    print(f"{'P_bloqueo':<25} {exp.pb_m:>12.6f} {exp.pb_t:>12.6f}")
    print(f"{'N° corridas':<25} {exp.n_corridas:>12}")
    print(f"{'IC95% L':<25} [{exp.L_m-1.96*exp.L_s/np.sqrt(exp.n_corridas):>.4f}, {exp.L_m+1.96*exp.L_s/np.sqrt(exp.n_corridas):>.4f}]")
    print(f"{'IC95% W':<25} [{exp.W_m-1.96*exp.W_s/np.sqrt(exp.n_corridas):>.4f}, {exp.W_m+1.96*exp.W_s/np.sqrt(exp.n_corridas):>.4f}]")
    print(f"{'='*85}")


def mostrar_tabla_completa(resultados: dict):
    print(f"\n{'='*115}")
    print("RESUMEN COMPLETO — EXPERIMENTO FACTORIAL M/M/1/K")
    print(f"{'='*115}")
    header = f"{'K':>4} {'ρ':>6} {'L_sim':>8} {'L_teo':>8} {'Lq_sim':>8} {'Lq_teo':>8} {'W_sim':>8} {'W_teo':>8} {'Util':>8} {'P_bloq':>8}"
    print(header)
    print(f"{'-'*115}")
    for (K, ratio), exp in sorted(resultados.items()):
        print(f"{K:>4} {ratio:>6.2f} {exp.L_m:>8.4f} {exp.L_t:>8.4f} {exp.Lq_m:>8.4f} {exp.Lq_t:>8.4f} {exp.W_m:>8.4f} {exp.W_t:>8.4f} {exp.util_m:>8.4f} {exp.pb_m:>8.4f}")
    print(f"{'='*115}")


# =============================================================================
# 6. GRAFICOS
# =============================================================================

def graficar_comparacion(resultados: dict, save_path: Optional[str] = None):
    ratios = sorted(set(r for (_, r) in resultados.keys()))
    Ks = sorted(set(k for (k, _) in resultados.keys()))

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    metricas = [
        ('L', 'L (clientes en sistema)', 'N° clientes'),
        ('Lq', 'Lq (clientes en cola)', 'N° clientes'),
        ('W', 'W (tiempo en sistema)', 'Tiempo'),
        ('Wq', 'Wq (tiempo en cola)', 'Tiempo'),
        ('utilizacion', 'Utilizacion del servidor', 'Proporcion'),
        ('P_block', 'Probabilidad de bloqueo', 'Probabilidad'),
    ]

    sim_attr = {
        'L': 'L_m', 'Lq': 'Lq_m', 'W': 'W_m', 'Wq': 'Wq_m',
        'utilizacion': 'util_m', 'P_block': 'pb_m'
    }
    teo_attr = {
        'L': 'L_t', 'Lq': 'Lq_t', 'W': 'W_t', 'Wq': 'Wq_t',
        'utilizacion': 'util_t', 'P_block': 'pb_t'
    }
    for ax, (attr, title, ylabel) in zip(axes, metricas):
        for K in Ks:
            sim_vals = []
            teo_vals = []
            for r in ratios:
                exp = resultados[(K, r)]
                sim_vals.append(getattr(exp, sim_attr[attr]))
                teo_vals.append(getattr(exp, teo_attr[attr]))
            ax.plot(ratios, sim_vals, 'o-', label=f'Sim K={K}', ms=5)
            ax.plot(ratios, teo_vals, 's--', label=f'Teo K={K}', ms=4, alpha=0.6)
        ax.set_xlabel('ρ = λ/μ')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def graficar_convergencia(resultados: dict, K_sel: int = 10, save_path: Optional[str] = None):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    colores = plt.cm.viridis(np.linspace(0.2, 0.9, 5))

    for idx, (ratio) in enumerate(sorted(set(r for (k, r) in resultados if k == K_sel))):
        exp = resultados[(K_sel, ratio)]
        corr = exp.corridas[0]
        if len(corr.t_check) > 1:
            axes[0].plot(corr.t_check, corr.L_t, color=colores[idx],
                         label=f'ρ={ratio:.2f}')
            axes[1].plot(corr.t_check, corr.W_t, color=colores[idx],
                         label=f'ρ={ratio:.2f}')

    for ax in axes[:2]:
        ax.axhline(y=0, color='gray', lw=0.5)
        ax.set_xlabel('Tiempo de simulacion')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel('L(t) promedio acumulado')
    axes[0].set_title('Convergencia de L')
    axes[1].set_ylabel('W(t) promedio acumulado')
    axes[1].set_title('Convergencia de W')

    # Distribucion Pn
    K_mostrar = K_sel
    for ratio in [0.5, 0.75, 1.0]:
        exp = resultados[(K_mostrar, ratio)]
        teor = teoricas_mm1k(exp.lam, exp.mu, K_mostrar)
        n_max = min(K_mostrar + 1, 15)
        ns = range(n_max)
        sim_pn = exp.corridas[0].Pn[:n_max]
        teo_pn = teor['Pn'][:n_max]
        axes[2].plot(ns, sim_pn, 'o-', label=f'Sim ρ={ratio:.2f}')
        axes[2].plot(ns, teo_pn, 's--', label=f'Teo ρ={ratio:.2f}', alpha=0.6)
    axes[2].set_xlabel('n (clientes en sistema)')
    axes[2].set_ylabel('Pn')
    axes[2].set_title(f'Distribucion Pn — K={K_mostrar}')
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def graficar_pn_vs_k(resultados: dict, save_path: Optional[str] = None):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    Ks = [5, 10, 50]
    colores = plt.cm.Set1(np.linspace(0, 0.8, 5))

    for ax_idx, ratio in enumerate([0.5, 1.0]):
        ax = axes[ax_idx]
        for Ki in Ks:
            exp = resultados[(Ki, ratio)]
            teor = teoricas_mm1k(exp.lam, exp.mu, Ki)
            ns = range(min(Ki + 1, 20))
            sim_pn = exp.corridas[0].Pn[:len(ns)]
            teo_pn = teor['Pn'][:len(ns)]
            ax.plot(ns, sim_pn, 'o-', label=f'Sim K={Ki}', ms=4)
            ax.plot(ns, teo_pn, 's--', label=f'Teo K={Ki}', ms=3, alpha=0.5)
        ax.set_xlabel('n (clientes en sistema)')
        ax.set_ylabel('Pn')
        ax.set_title(f'Distribucion Pn — ρ = {ratio}')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


# =============================================================================
# 7. MAIN / CLI
# =============================================================================

def demo_rapida():
    """Demostracion rapida con un solo experimento."""
    print("\n>>> DEMO RAPIDA M/M/1/K <<<\n")
    lam = float(input("  λ (tasa llegada) [0.8]: ") or "0.8")
    mu = float(input("  μ (tasa servicio) [1.0]: ") or "1.0")
    K = int(input("  K (capacidad) [10]: ") or "10")
    n_c = int(input("  N° corridas [10]: ") or "10")
    t_sim = float(input("  Tiempo sim [10000]: ") or "10000.0")
    warm = float(input("  Calentamiento [1000]: ") or "1000.0")

    print("\nEjecutando simulacion...")
    exp = experimento_mm1k(lam, mu, K, n_c, t_sim, warm)
    mostrar_tabla_experimento(exp)
    return exp


def main():
    parser = argparse.ArgumentParser(
        description='Simulador M/M/1/K — Cola con capacidad finita',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python mm1k_simulacion.py --demo
  python mm1k_simulacion.py --lam 0.8 --mu 1.0 --K 10 --corridas 20
  python mm1k_simulacion.py --completo --mu 1.0
  python mm1k_simulacion.py --graficos
        """)
    parser.add_argument('--demo', action='store_true', help='Modo interactivo')
    parser.add_argument('--lam', type=float, default=None, help='Tasa de llegada')
    parser.add_argument('--mu', type=float, default=1.0, help='Tasa de servicio')
    parser.add_argument('--K', type=int, default=None, help='Capacidad del sistema')
    parser.add_argument('--corridas', type=int, default=10, help='Numero de corridas')
    parser.add_argument('--tiempo', type=float, default=10000.0, help='Tiempo de simulacion')
    parser.add_argument('--warmup', type=float, default=1000.0, help='Periodo de calentamiento')
    parser.add_argument('--completo', action='store_true', help='Ejecutar experimento factorial completo')
    parser.add_argument('--graficos', action='store_true', help='Generar graficos')
    parser.add_argument('--output', type=str, default=None, help='Prefijo para guardar graficos')

    args = parser.parse_args()

    if args.demo:
        demo_rapida()
        return

    if args.completo:
        print("\n" + "="*60)
        print("EXPERIMENTO FACTORIAL COMPLETO M/M/1/K")
        print("="*60)
        print(f"μ = {args.mu}")
        print(f"Corridas por experimento: {args.corridas}")
        print(f"Tiempo de simulacion: {args.tiempo}")
        print(f"Calentamiento: {args.warmup}")
        print(f"Variando K: [0, 2, 5, 10, 50]")
        print(f"Variando ρ = λ/μ: [0.25, 0.50, 0.75, 1.00, 1.25]")
        print("="*60)

        resultados = experimento_completo(
            mu=args.mu, n_corridas=args.corridas,
            tiempo_sim=args.tiempo, calentamiento=args.warmup
        )
        mostrar_tabla_completa(resultados)

        if args.graficos:
            prefijo = args.output or "mm1k_resultados"
            graficar_comparacion(resultados, save_path=f"{prefijo}_comparacion.png")
            graficar_convergencia(resultados, K_sel=10, save_path=f"{prefijo}_convergencia.png")
            graficar_pn_vs_k(resultados, save_path=f"{prefijo}_pn.png")
            print(f"\nGraficos guardados como: {prefijo}_*.png")
    else:
        if args.lam is None or args.K is None:
            parser.print_help()
            print("\nERROR: Debe especificar --lam y --K (o usar --demo o --completo)")
            return

        exp = experimento_mm1k(
            args.lam, args.mu, args.K, args.corridas,
            args.tiempo, args.warmup
        )
        mostrar_tabla_experimento(exp)

        if args.graficos:
            resultados = {(args.K, args.lam/args.mu): exp}
            prefijo = args.output or f"mm1k_K{args.K}_r{args.lam/args.mu:.2f}"
            graficar_comparacion(resultados, save_path=f"{prefijo}_comp.png")
            print(f"Grafico guardado: {prefijo}_comp.png")


if __name__ == '__main__':
    main()
