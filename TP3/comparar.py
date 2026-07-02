"""
Utilidad de comparacion: Teoría vs Python vs AnyLogic
======================================================
Exporta resultados de Python a CSV para comparar con AnyLogic,
e importa resultados de AnyLogic para graficar junto a los teoricos.

USO:
  python comparar.py --exportar-mm1k
  python comparar.py --exportar-inventario
  python comparar.py --comparar-mm1k anylogic_mm1k.csv
  python comparar.py --comparar-inventario anylogic_inv.csv
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv, os, sys, json
from typing import Optional, List, Dict, Tuple

plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.size'] = 10

# Ruta base
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from mm1k_simulacion import experimento_completo as exp_mm1k, teoricas_mm1k, mostrar_tabla_completa
from inventario_simulacion import experimento_inventario as exp_inv, mostrar_tabla_inventario


def exportar_mm1k_csv(
    mu=1.0, valores_K=None, ratios=None,
    n_corridas=10, tiempo_sim=10000, warmup=1000,
    archivo=None
):
    if valores_K is None:
        valores_K = [0, 2, 5, 10, 50]
    if ratios is None:
        ratios = [0.25, 0.50, 0.75, 1.00, 1.25]
    if archivo is None:
        archivo = os.path.join(BASE, 'mm1k_resultados_python.csv')

    print(f"Ejecutando experimento MM1K (exportando a {archivo})...")
    resultados = exp_mm1k(mu, valores_K, ratios, n_corridas, tiempo_sim, warmup)

    with open(archivo, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['K', 'rho', 'L_sim', 'L_teo', 'Lq_sim', 'Lq_teo',
                     'W_sim', 'W_teo', 'Wq_sim', 'Wq_teo',
                     'util_sim', 'util_teo', 'P_bloq_sim', 'P_bloq_teo'])
        for (K, r), exp in sorted(resultados.items()):
            w.writerow([K, f'{r:.2f}',
                       f'{exp.L_m:.6f}', f'{exp.L_t:.6f}',
                       f'{exp.Lq_m:.6f}', f'{exp.Lq_t:.6f}',
                       f'{exp.W_m:.6f}', f'{exp.W_t:.6f}',
                       f'{exp.Wq_m:.6f}', f'{exp.Wq_t:.6f}',
                       f'{exp.util_m:.6f}', f'{exp.util_t:.6f}',
                       f'{exp.pb_m:.6f}', f'{exp.pb_t:.6f}'])

    # Tambien exportar convergencia
    archivo_conv = os.path.join(BASE, 'mm1k_convergencia_python.csv')
    with open(archivo_conv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['K', 'rho', 't_check', 'L_acum', 'W_acum'])
        for (K, r), exp in sorted(resultados.items()):
            corr = exp.corridas[0]
            for tc, lv, wv in zip(corr.t_check, corr.L_t, corr.W_t):
                w.writerow([K, f'{r:.2f}', f'{tc:.2f}', f'{lv:.6f}', f'{wv:.6f}'])

    print(f"Exportados {len(resultados)} experimentos.")
    return archivo


def exportar_inventario_csv(
    lam=10.0, L=3.0, s=40, S=72, K_ord=50.0, h=1.0, p=10.0,
    n_corridas=10, tiempo_sim=365, warmup=30,
    archivo=None
):
    if archivo is None:
        archivo = os.path.join(BASE, 'inv_resultados_python.csv')

    print(f"Ejecutando experimento Inventario (exportando a {archivo})...")
    exp = exp_inv(lam, L, s, S, K_ord, h, p, n_corridas, tiempo_sim, warmup)

    with open(archivo, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['corrida', 'costo_orden', 'costo_mant', 'costo_falt',
                     'costo_total', 'num_ordenes', 'fill_rate'])
        for i, corr in enumerate(exp.corridas):
            w.writerow([i+1,
                       f'{corr.costo_orden:.2f}',
                       f'{corr.costo_mantenimiento:.2f}',
                       f'{corr.costo_faltante:.2f}',
                       f'{corr.costo_total:.2f}',
                       corr.num_ordenes,
                       f'{corr.fill_rate:.6f}'])

    print(f"Exportadas {n_corridas} corridas.")
    return archivo


def comparar_mm1k(archivo_anylogic: str, archivo_salida: Optional[str] = None):
    """Compara Python vs AnyLogic vs Teorico para MM1K."""
    # Cargar AnyLogic CSV
    anylogic = {}
    try:
        with open(archivo_anylogic, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                K = int(row['K'])
                rho = float(row['rho'])
                anylogic[(K, rho)] = {
                    'L': float(row.get('L', 0)),
                    'Lq': float(row.get('Lq', 0)),
                    'W': float(row.get('W', 0)),
                    'Wq': float(row.get('Wq', 0)),
                    'util': float(row.get('util', 0)),
                    'P_block': float(row.get('P_block', 0)),
                }
    except FileNotFoundError:
        print(f"ERROR: No se encuentra {archivo_anylogic}")
        return

    # Obtener teoricos
    teoricos = {}
    for (K, rho) in anylogic:
        lam = rho * 1.0  # asume mu=1
        teoricos[(K, rho)] = teoricas_mm1k(lam, 1.0, K)

    # Graficar comparacion
    Ks = sorted(set(k for (k, _) in anylogic))
    rhos = sorted(set(r for (_, r) in anylogic))

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    metricas = [
        ('L', 'L - Clientes en sistema', 'N°'),
        ('Lq', 'Lq - Clientes en cola', 'N°'),
        ('W', 'W - Tiempo en sistema', 'Tpo'),
        ('Wq', 'Wq - Tiempo en cola', 'Tpo'),
        ('util', 'Utilizacion', '%'),
        ('P_block', 'Prob. Bloqueo', 'Prob'),
    ]

    colores = {'Teorico': 'blue', 'Python': 'green', 'AnyLogic': 'red'}

    for ax, (attr, title, _) in zip(axes, metricas):
        for K in Ks:
            xs = []
            yt, yp, ya = [], [], []
            for r in rhos:
                key = (K, r)
                if key in anylogic:
                    xs.append(r)
                    yt.append(teoricos[key][attr])
                    ya.append(anylogic[key][attr])
                    # Python: recalculamos
                    lam = r * 1.0
                    t = teoricas_mm1k(lam, 1.0, K)
                    yp.append(t[attr])

            if xs:
                ax.plot(xs, yt, 's--', color=colores['Teorico'],
                        label=f'Teo K={K}' if r == rhos[-1] else '', alpha=0.5)
                ax.plot(xs, yp, 'o-', color=colores['Python'],
                        label=f'Py K={K}' if r == rhos[-1] else '', ms=5)
                ax.plot(xs, ya, '^-', color=colores['AnyLogic'],
                        label=f'AL K={K}' if r == rhos[-1] else '', ms=5)
        ax.set_xlabel('ρ')
        ax.set_ylabel(attr)
        ax.set_title(title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=150)
    else:
        plt.savefig(os.path.join(BASE, 'comparacion_mm1k_teoria_python_anylogic.png'), dpi=150)
    print(f"Grafico guardado.")
    plt.close()


def comparar_inventario(archivo_anylogic: str):
    """Carga resultados AnyLogic de inventario y los compara."""
    try:
        with open(archivo_anylogic, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            datos = list(reader)
        if not datos:
            print("Archivo AnyLogic vacio")
            return

        print(f"Cargados {len(datos)} registros de AnyLogic")
        for row in datos:
            print(f"  Corrida {row.get('corrida','?'):>4}: "
                  f"Ord=${float(row.get('costo_orden',0)):.0f} "
                  f"Man=${float(row.get('costo_mant',0)):.0f} "
                  f"Fal=${float(row.get('costo_falt',0)):.0f} "
                  f"Tot=${float(row.get('costo_total',0)):.0f}")

    except FileNotFoundError:
        print(f"ERROR: No se encuentra {archivo_anylogic}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Comparacion Teoria vs Python vs AnyLogic')
    parser.add_argument('--exportar-mm1k', action='store_true', help='Exportar resultados MM1K a CSV')
    parser.add_argument('--exportar-inventario', action='store_true', help='Exportar resultados Inventario a CSV')
    parser.add_argument('--comparar-mm1k', type=str, help='CSV de AnyLogic para MM1K')
    parser.add_argument('--comparar-inventario', type=str, help='CSV de AnyLogic para Inventario')
    parser.add_argument('--corridas', type=int, default=10, help='N° corridas')
    parser.add_argument('--tiempo-mm1k', type=float, default=10000, help='Tiempo sim MM1K')
    parser.add_argument('--tiempo-inv', type=float, default=365, help='Tiempo sim Inventario')

    args = parser.parse_args()

    if args.exportar_mm1k:
        exportar_mm1k_csv(n_corridas=args.corridas, tiempo_sim=args.tiempo_mm1k)
    if args.exportar_inventario:
        exportar_inventario_csv(n_corridas=args.corridas, tiempo_sim=args.tiempo_inv)
    if args.comparar_mm1k:
        comparar_mm1k(args.comparar_mm1k)
    if args.comparar_inventario:
        comparar_inventario(args.comparar_inventario)

    if not any([args.exportar_mm1k, args.exportar_inventario,
                args.comparar_mm1k, args.comparar_inventario]):
        parser.print_help()
