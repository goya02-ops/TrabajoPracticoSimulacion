
Para ejecutar
venv/bin/python mm1_simulacion.py
y elegir opciones

MM1

"""
Simulador de Inventario (s, S) — Modelo de Law & Kelton (fiel al libro)
=========================================================================
Puerto a Python del ejemplo clasico de Law & Kelton, "Simulation Modeling
and Analysis", Cap. 1.5 (Figs. 1.32 a 1.43). Es el mismo modelo que
`inventario_simulacion.py`, pero fiel a la logica exacta del codigo en C
del libro, en vez de la version simplificada de revision continua.

MODELO (arquitectura identica a la del libro, Figs. 1.35-1.39):
  - Estado: UNA sola variable de inventario fisico (inv_level, puede ser
    negativo = faltante). NO hay posicion de inventario separada ni lista
    de ordenes: como en el codigo original, solo puede haber UNA orden
    pendiente a la vez (variables escalares amount/t_arribo, igual que
    time_next_event[1] en el libro). Esto es seguro porque, con
    T_revision=30 dias y lead time maximo de 5 dias, cualquier orden
    llega mucho antes de la siguiente revision — nunca hay superposicion.
  - Demanda: interdemanda exponencial de media mean_interdemand (dias).
    Tamaño de demanda: distribucion discreta {1,2,3,4} unidades por
    cliente con probabilidades {1/6, 1/3, 1/3, 1/6} — la distribucion
    EXACTA del ejemplo del libro (Fig. 1.38, funcion demand()).
  - Lead time: aleatorio, Uniforme(minlag, maxlag) dias, sorteado en cada
    orden (no un unico valor para toda la simulacion).
  - Revision PERIODICA cada T_revision dias (en el libro esta hardcodeado
    a "1 mes exacto": time_next_event[4] = sim_time + 1.0). La primera
    revision es en t=T_revision, no en t=0 (el libro no evalua en t=0
    porque el inventario arranca en S y nunca dispara una orden ahi).
  - Condicion de orden: si inv_level < smalls (estricto, chequeado
    directamente sobre el fisico, igual que el libro — no hace falta
    posicion porque nunca hay ordenes superpuestas), se ordena
    bigs - inv_level unidades.
  - Backorders permitidos (inv_level negativo = faltante).
  - El libro NO descarta un periodo de warmup y corre una UNICA simulacion
    larga por cada politica (s,S) — no hace replicas con semillas distintas.

NOTA SOBRE UNIDADES: el libro trabaja en MESES; aca todo esta en DIAS para
usar el mismo horizonte de 365 dias que el resto del TP. Los parametros de
demanda, lead time y costos son los de la consigna del TP (ver mas abajo),
no la conversion literal del ejemplo del libro — pero la MECANICA del
modelo (arquitectura de una sola orden, distribucion de demanda, momento
de la primera revision, chequeo de reorden sobre inv_level) es identica
a la del libro.

AGREGADOS respecto al libro (para cumplir la consigna del TP):
  - Multiples corridas (>=10) con semillas distintas, ya que el libro corre
    una unica simulacion larga por politica y el TP pide minimo 10 corridas.
  - Historial en el tiempo de costos e inventario, para graficar.
  - Una seccion de valores teoricos aproximados (el libro no calcula ningun
    valor teorico — este ejemplo existe justamente porque no tiene solucion
    cerrada; por eso decimos "aproximado").

JUSTIFICACION DE PARAMETROS (consigna del TP):
------------------------------------------------------------------------
  inv_inicial      = S und        Nivel inicial de inventario (= S de cada experimento)
  mean_interdemand = 0.1 dias     lambda = 10 clientes/dia
  minlag, maxlag   = 2, 5 dias    Lead time aleatorio Uniforme(2,5) dias (prom. 3.5 dias)
  T_revision       = 30 dias      Revision periodica mensual (valor del libro, "1 mes")
  K_ord (setup)    = $100         Costo fijo por orden
  c (incremental)  = $3/und       (no especificado en la consigna; se mantiene el valor previo)
  h (holding)      = $2/und/dia   Costo de mantenimiento
  p (shortage,pi)  = $50/und/dia  Costo de faltante
  num_dias         = 365 dias     Horizonte de simulacion (1 anho)

  Con T_revision=30, el periodo de proteccion (T_revision + lag_medio =
  33.5 dias) acumula ~837 unidades de demanda esperada — por eso s,S se
  recalibraron a esta escala (ver formula en MARCO TEORICO mas abajo).
  Cada experimento tiene un costo claramente dominante (~70%), sin que
  acapare el 100% del total (el otro queda como secundario, no nulo):
  Exp 1 (Conservadora): s=600, S=1350  Mantenimiento domina (~71%),
                                       Faltante secundario (~25%).
  Exp 2 (Ajustada/JIT):  s=350, S=1100 Faltante domina (~70%),
                                       Mantenimiento secundario (~28%).

MARCO TEORICO (aproximacion, el libro no da una formula cerrada):
  Periodo de proteccion pp = T_revision + lag_medio.
  mu_X, var_X: media y varianza del tamaño de demanda, distribucion del
  libro {1,2,3,4} con probs {1/6,1/3,1/3,1/6}:
      mu_X = 2.5, var_X = 11/12 = 0.9167
      mu_pp    = lam * pp * mu_X            (lam = 1/mean_interdemand)
      var_pp   = lam * pp * (var_X + mu_X^2)  (Poisson compuesta)
      s_teo    = mu_pp + z*sqrt(var_pp)       (z=1.64 para ~95% servicio)

  Inventario fisico promedio (base del costo de Mantenimiento): la
  aproximacion lineal clasica Q/2 + (s - mu_pp) puede dar negativa con
  politicas agresivas (s << mu_pp) — pero el inventario fisico nunca es
  negativo (eso es faltante). Se corrige sumando faltante_ciclo (el
  mismo termino usado para el costo de Faltante):
      inv_prom = Q/2 + (s - mu_pp) + faltante_ciclo >= 0   (siempre, por
      identidad: (s-mu_pp) + faltante_ciclo = sigma_pp*E[max(Z,0)] >= 0)
"""
