# TP1.2 — Simulación de Estrategias de Apuesta (Ruleta Europea)

Simulación computacional de 4 estrategias de apuesta aplicadas a la ruleta europea (0-36), apostando siempre a color rojo (18/37 de probabilidad).

## Requisitos

- Python 3.10+
- `matplotlib`: `pip install matplotlib`

## Uso

```bash
python3 programa.py -c 500 -s i -a 1000 -i 20
```

### Argumentos

| Flag                 | Descripción                                                           | Default |
| -------------------- | --------------------------------------------------------------------- | ------- |
| `-c`, `--tiradas`    | Cantidad de tiradas                                                   | 10000   |
| `-s`, `--estrategia` | Estrategia: `i` Fibonacci, `d` d'Alembert, `m` Martingala, `p` Paroli | `i`     |
| `-a`, `--capital`    | Capital inicial: número para finito, `i` para infinito                | 10000   |
| `-i`, `--apuesta`    | Apuesta inicial                                                       | 18      |

Solo se ejecuta **una** estrategia por invocación, la indicada con `-s`.

## Estructura del proyecto

```
TP1.2/
├── programa.py        ← Punto de entrada, CLI y orquestación
├── estrategias.py     ← 4 estrategias con sus callbacks + constante FIB
├── motor.py           ← Motor de simulación genérico (función simular())
├── graficos.py        ← Generación de gráficos con matplotlib
├── constantes.py      ← Constantes del modelo (ruleta europea)
├── image/             ← Directorio de salida de los gráficos PNG
└── README.md
```

## Estrategias

| Nombre     | Flag | Lógica                                                                       |
| ---------- | ---- | ---------------------------------------------------------------------------- |
| Fibonacci  | `i`  | Secuencia Fibonacci: tras perder se avanza, tras ganar se retrocede 2 pasos  |
| d'Alembert | `d`  | Progresión lineal: +1 unidad al perder, −1 al ganar (mínimo apuesta inicial) |
| Martingala | `m`  | Se duplica la apuesta tras cada pérdida; al ganar se reinicia                |
| Paroli     | `p`  | Se duplica tras ganar (hasta 3 veces consecutivas); al perder se reinicia    |

## Gráficos generados (3 por estrategia)

Todos se guardan en `image/`:

| Archivo                              | Descripción                                                                         |
| ------------------------------------ | ----------------------------------------------------------------------------------- |
| `flujocaja_{estrategia}.png`         | Evolución del capital a lo largo de las tiradas                                     |
| `evolucionapuestas_{estrategia}.png` | Monto apostado en cada tirada                                                       |
| `frecuencia_{estrategia}.png`        | Frecuencia relativa acumulada de aciertos (rojos), con línea de referencia en 18/37 |

`plt.show()` abre una ventana interactiva por cada gráfico; la ejecución se pausa hasta cerrarla. Usar `MPLBACKEND=Agg` para correr sin interfaz gráfica.

## Capital

- Si `-a i`: capital infinito (`float('inf')`), nunca se llega a bancarrota. El gráfico de flujo de caja omite la línea de referencia.
- Si `-a <número>`: capital finito; la simulación corta si el capital disponible es menor a la apuesta requerida.

## Modelo de la ruleta

| Parámetro            | Valor                  |
| -------------------- | ---------------------- |
| Tipo                 | Europea (un solo cero) |
| Números              | 0 al 36 (37 total)     |
| Rojo                 | 18 números             |
| Negro                | 18 números             |
| Verde                | 0                      |
| Pago a pleno         | 36 a 1                 |
| Probabilidad de rojo | 18/37 ≈ 0.4865         |
| Ventaja de la casa   | 2.7%                   |