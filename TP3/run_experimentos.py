import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from inventario_simulacion import (
    experimento_inventario,
    mostrar_tabla_inventario,
    graficar_costos,
    graficar_comparacion_runs,
)
import numpy as np

CARPETA = "imagenes/inventario"
os.makedirs(CARPETA, exist_ok=True)

# ─── EXPERIMENTO 1 ───────────────────────────────────────────────────────────
print("\n" + "="*85)
print("EXPERIMENTO 1 — Política conservadora (alto nivel de servicio)")
print("="*85)
exp1 = experimento_inventario(
    lam=10, L=3, s=30, S=80,
    K_ord=32, c=3, h=1, p=5,
    n_corridas=10, tiempo_sim=365, calentamiento=30
)
mostrar_tabla_inventario(exp1)
graficar_costos(exp1, save_path=os.path.join(CARPETA, "exp1_conservadora_dashboard.png"))
graficar_comparacion_runs(exp1, save_path=os.path.join(CARPETA, "exp1_conservadora_corridas.png"))
print("Graficos Experimento 1 guardados.")

# ─── EXPERIMENTO 2 ───────────────────────────────────────────────────────────
print("\n" + "="*85)
print("EXPERIMENTO 2 — Política JIT (bajo nivel de stock)")
print("="*85)
exp2 = experimento_inventario(
    lam=10, L=3, s=10, S=30,
    K_ord=32, c=3, h=1, p=5,
    n_corridas=10, tiempo_sim=365, calentamiento=30
)
mostrar_tabla_inventario(exp2)
graficar_costos(exp2, save_path=os.path.join(CARPETA, "exp2_jit_dashboard.png"))
graficar_comparacion_runs(exp2, save_path=os.path.join(CARPETA, "exp2_jit_corridas.png"))
print("Graficos Experimento 2 guardados.")

# ─── COMPARACIÓN FINAL ───────────────────────────────────────────────────────
print("\n" + "="*85)
print("COMPARACIÓN ENTRE EXPERIMENTOS")
print("="*85)
print(f"{'Métrica':<35} {'Exp 1 — Conservadora':>20} {'Exp 2 — JIT':>12}")
print("-"*68)
print(f"{'s (punto de reorden)':<35} {exp1.s:>20} {exp2.s:>12}")
print(f"{'S (nivel máximo)':<35} {exp1.S:>20} {exp2.S:>12}")
print(f"{'Costo de Orden (total anual)':<35} {exp1.co_m:>20.2f} {exp2.co_m:>12.2f}")
print(f"{'Costo Mantenimiento (total anual)':<35} {exp1.cm_m:>20.2f} {exp2.cm_m:>12.2f}")
print(f"{'Costo Faltante (total anual)':<35} {exp1.cf_m:>20.2f} {exp2.cf_m:>12.2f}")
print(f"{'Costo TOTAL anual':<35} {exp1.ct_m:>20.2f} {exp2.ct_m:>12.2f}")
print(f"{'N° Ordenes promedio':<35} {exp1.num_ord_m:>20.1f} {exp2.num_ord_m:>12.1f}")
print(f"{'Fill Rate (nivel de servicio)':<35} {exp1.fill_rate_m:>20.4f} {exp2.fill_rate_m:>12.4f}")
print("="*68)

# Ganador por costo total
if exp1.ct_m < exp2.ct_m:
    diff = exp2.ct_m - exp1.ct_m
    print(f"\n➜ MENOR COSTO TOTAL: Experimento 1 (Conservadora) por ${diff:.2f}/año")
else:
    diff = exp1.ct_m - exp2.ct_m
    print(f"\n➜ MENOR COSTO TOTAL: Experimento 2 (JIT) por ${diff:.2f}/año")

# Coherencia con lo esperado
print("\n── Coherencia con lo esperado ──")
if exp1.cm_m > exp2.cm_m:
    print(f"✓ Exp1 tiene MAYOR costo de mantenimiento (${exp1.cm_m:.0f} vs ${exp2.cm_m:.0f}) — correcto: stock alto.")
else:
    print(f"✗ Inconsistencia: Exp1 debería tener mayor costo de mantenimiento.")

if exp2.cf_m > exp1.cf_m:
    print(f"✓ Exp2 tiene MAYOR costo de faltante (${exp2.cf_m:.0f} vs ${exp1.cf_m:.0f}) — correcto: JIT arriesga quiebres.")
else:
    print(f"✗ Inconsistencia: Exp2 debería tener mayor costo de faltante.")

if exp1.fill_rate_m > exp2.fill_rate_m:
    print(f"✓ Exp1 tiene MAYOR fill rate ({exp1.fill_rate_m:.4f} vs {exp2.fill_rate_m:.4f}) — correcto: política conservadora.")
else:
    print(f"✗ Inconsistencia: Exp1 debería tener mayor fill rate.")
