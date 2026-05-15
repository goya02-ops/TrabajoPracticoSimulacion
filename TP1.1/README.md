# Simulación de Ruleta Europea

Trabajo práctico de la materia Simulación — modelado y análisis de una ruleta europea (0-36) mediante simulación computacional en Python.

## Requerimientos

- Python 3.10+
- matplotlib: `pip install matplotlib`

## Uso rápido

```bash
# Con valores por defecto (10000 tiradas, 200 corridas, número 18)
python3 programa.py

# Con parámetros personalizados
python3 programa.py -c 1000 -n 10 -e 7
```

### Argumentos

| Flag | Descripción | Default |
|------|-------------|---------|
| `-c`, `--tiradas` | Cantidad de tiradas por corrida | 10000 |
| `-n`, `--corridas` | Cantidad de corridas | 200 |
| `-e`, `--elegido` | Número elegido para análisis (0-36) | 18 |

## Estructura del proyecto

```
TP1.1/
├── programa.py          ← Punto de entrada, CLI y orquestación
├── motor.py             ← Motor de simulación (tiradas, corridas)
├── calculos.py          ← Cálculos estadísticos O(n) acumulados
├── graficos.py          ← Generación de gráficos con matplotlib
├── CONSTANTES.py        ← Constantes del modelo (ruleta europea 0-36)
├── image/               ← Directorio de salida de los gráficos PNG
├── README.md
└── enunciado.md         ← Enunciado original del TP
```

## Gráficos generados (8)

Todos se guardan en `image/`:

| # | Archivo | Descripción | Concepto |
|---|---------|-------------|----------|
| 1 | `frecuencia_relativa_concatenada.png` | Frecuencia relativa acumulada de todas las corridas unidas como secuencia continua | Ley de los Grandes Números |
| 2 | `frecuencia_relativa_multiples.png` | Frecuencia relativa de cada corrida superpuestas en un solo gráfico | Convergencia por corrida |
| 3 | `media_acumulada_concatenada.png` | Media acumulada de todas las corridas concatenadas (ref: 18.0) | Esperanza matemática |
| 4 | `varianza_acumulada_concatenada.png` | Varianza acumulada concatenada (ref: 114.0) | Dispersión |
| 5 | `desvio_acumulada_concatenada.png` | Desvío estándar acumulado concatenado (ref: 10.677) | Dispersión |
| 6 | `histograma_resultados.png` | Distribución de frecuencias absolutas de la primera corrida | Uniformidad |
| 7 | `distribucion_medias.png` | Histograma de medias finales de todas las corridas | Teorema Central del Límite |
| 8 | `boxplot_medias.png` | Diagrama de caja de las medias finales | Dispersión entre corridas |

## Modelo de la ruleta

| Parámetro | Valor |
|-----------|-------|
| Tipo | Europea (un solo cero) |
| Números | 0 al 36 (37 total) |
| Probabilidad por número | 1/37 ≈ 0.027027 |
| Media teórica E[X] | 18.0 |
| Varianza teórica Var(X) | 114.0 |
| Desvío teórico σ | √114 ≈ 10.677 |
| Pago a pleno | 36 a 1 |
| Ventaja de la casa | 2.7% |

## Conceptos teóricos

### Ley de los Grandes Números

A medida que el número de tiradas aumenta, la frecuencia relativa de cada número converge a su probabilidad teórica 1/37. Esto se observa en los gráficos de frecuencia relativa concatenada.

### Esperanza Matemática

Para una distribución uniforme discreta U(0, 36):

$$E[X] = \frac{\sum_{i=0}^{36} i}{37} = \frac{666}{37} = 18$$

### Varianza y Desvío Estándar

$$Var(X) = \frac{n^2 - 1}{12} = \frac{37^2 - 1}{12} = 114$$

$$\sigma = \sqrt{114} \approx 10.677$$

### Teorema Central del Límite

La distribución de las medias muestrales de múltiples corridas converge a una distribución normal N(μ, σ/√n), donde μ = 18 y σ = √114, independientemente de que la distribución original sea uniforme.

## Salida de ejemplo

```
Media de las medias: 17.9592 (esperada: 18.0)
Desvío estándar de las medias: 0.3562
Media teórica: 18.0
```

## Notas técnicas

### Uso de la librería `statistics`

En `calculos.py` usamos la librería `statistics` de Python solo cuando necesitamos un **valor final** (no acumulativo):

- `media_final()` → usa `statistics.mean()` ✓

**No usamos `statistics` en `todos_los_estadisticos()`** porque:
- Necesitamos valores **acumulativos** en cada punto de la secuencia (para los gráficos de convergencia)
- Usar `statistics.mean(data[:i])` en cada iteración sería O(n²) 
- El cálculo manual con sumas acumulativas es O(n), mucho más eficiente

Para 2,000,000 de datos: O(n) = ~2M operaciones vs O(n²) = ~4 billones de operaciones.

## Enunciado

El enunciado completo del trabajo práctico se encuentra en `enunciado.md`.
