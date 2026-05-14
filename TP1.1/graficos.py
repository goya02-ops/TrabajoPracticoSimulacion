import matplotlib.pyplot as plt
from CONSTANTES import (
    PROBABILIDAD_TEORICA,
    MEDIA_TEORICA,
    VARIANZA_TEORICA,
    DESVIO_TEORICO,
)
RUTA_GUARDADO = 'graficas/'


def graficar_histograma(resultados, num_corridas, tiradas_por_corrida):
    total = len(resultados)
    plt.figure(figsize=(12, 6))
    counts = [resultados.count(i) for i in range(37)]
    colors = [plt.cm.tab20(i / 37) for i in range(37)]
    plt.bar(range(37), counts, color=colors, edgecolor='black')
    plt.title(f'Histograma de resultados — {num_corridas} corridas x {tiradas_por_corrida:,} tiradas ({total:,} total)')
    plt.xlabel('Número')
    plt.ylabel('Frecuencia absoluta')
    plt.xticks(range(37), rotation=90)
    linea_teorica = total * PROBABILIDAD_TEORICA
    plt.axhline(y=linea_teorica, color='r', linestyle='--',
                label=f'Frecuencia teórica ≈ {linea_teorica:.1f}')
    plt.legend()
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/histograma_resultados.png')
    plt.show()


def graficar_distribucion_medias(medias, num_corridas, tiradas_por_corrida):
    plt.figure(figsize=(10, 6))
    plt.hist(medias, bins=30, color='skyblue', edgecolor='black')
    plt.axvline(MEDIA_TEORICA, color='r',
                linestyle='--', label='Media Teórica')
    plt.title(
        f'Distribución de las medias finales — {num_corridas} corridas x {tiradas_por_corrida:,} tiradas')
    plt.xlabel('Media final por corrida')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/distribucion_medias.png')
    plt.show()


def graficar_boxplot_medias(medias, num_corridas, tiradas_por_corrida):
    plt.figure(figsize=(8, 6))
    plt.boxplot(medias, patch_artist=True,
                boxprops=dict(facecolor='lightblue'))
    plt.axhline(y=MEDIA_TEORICA, color='r',
                linestyle='--', label='Media Teórica')
    plt.title(
        f'Diagrama de caja y bigote de las medias finales — {num_corridas} corridas x {tiradas_por_corrida:,} tiradas')
    plt.xlabel('Medias finales por corrida')
    plt.ylabel('Media final por corrida')
    plt.xticks([1], ['Medias'])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/boxplot_medias.png')
    plt.show()


def graficar_frecuencia_relativa_concatenada(frec_acumulada, numero_elegido, num_corridas, tiradas_por_corrida):
    """Gráfico único: frecuencia relativa acumulada de todas las corridas concatenadas."""
    plt.figure(figsize=(14, 7))

    # Submuestreo si hay >100K puntos para performance
    max_puntos = 100000
    step = max(1, len(frec_acumulada) // max_puntos)
    x_sub = range(1, len(frec_acumulada) + 1, step)
    y_sub = frec_acumulada[::step]

    plt.plot(x_sub, y_sub, color='steelblue', linewidth=0.8, alpha=0.8,
             label=f'Frecuencia observada del número {numero_elegido}')

    plt.axhline(y=PROBABILIDAD_TEORICA, color='red', linestyle='--',
                linewidth=2, label=f'Probabilidad teórica: {PROBABILIDAD_TEORICA:.4f}')

    plt.title(
        f'Frecuencia Relativa Acumulada — {num_corridas} corridas x {tiradas_por_corrida:,} tiradas')
    plt.xlabel('Número de tirada (acumulado de todas las corridas)')
    plt.ylabel('Frecuencia relativa')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f'{RUTA_GUARDADO}/frecuencia_relativa_concatenada.png', dpi=150)
    plt.show()


def graficar_frecuencia_relativa_multiples(todas_frec_relativa, n_corridas):
    """Gráfico con N líneas: una por cada corrida, superpuestas."""
    plt.figure(figsize=(14, 7))

    colores = plt.cm.tab10.colors
    ejex = range(1, len(todas_frec_relativa[0]) + 1)

    for i, frec in enumerate(todas_frec_relativa):
        plt.plot(ejex, frec, color=colores[i % 10],
                 linewidth=0.8, alpha=0.7, label=f'Corrida {i + 1}')

    plt.axhline(y=PROBABILIDAD_TEORICA, color='black', linestyle='--',
                linewidth=2, label=f'Probabilidad teórica: {PROBABILIDAD_TEORICA:.4f}')

    plt.title(
        f'Frecuencia Relativa Acumulada — {n_corridas} corridas superpuestas')
    plt.xlabel('Número de tirada')
    plt.ylabel('Frecuencia relativa')
    plt.legend(loc='center left', bbox_to_anchor=(
        1.02, 0.5), fontsize=8, framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/frecuencia_relativa_multiples.png',
                dpi=150, bbox_inches='tight')
    plt.show()


def _graficar_concatenado(datos, valor_teorico, titulo, etiqueta_y, nombre_archivo, num_corridas, tiradas_por_corrida):
    """Función genérica para gráficos concatenados con submuestreo."""
    plt.figure(figsize=(14, 7))

    max_puntos = 100000
    step = max(1, len(datos) // max_puntos)
    x_sub = range(1, len(datos) + 1, step)
    y_sub = datos[::step]

    plt.plot(x_sub, y_sub, color='steelblue', linewidth=0.8, alpha=0.8,
             label=f'Valor observado')

    plt.axhline(y=valor_teorico, color='red', linestyle='--',
                linewidth=2, label=f'Valor teórico: {valor_teorico:.4f}')

    plt.title(
        f'{titulo} — {num_corridas} corridas x {tiradas_por_corrida:,} tiradas')
    plt.xlabel('Número de tirada (acumulado de todas las corridas)')
    plt.ylabel(etiqueta_y)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{RUTA_GUARDADO}/{nombre_archivo}', dpi=150)
    plt.show()


def graficar_media_acumulada_concatenada(media_concat, num_corridas, tiradas_por_corrida):
    _graficar_concatenado(
        media_concat, MEDIA_TEORICA,
        'Media Acumulada Concatenada',
        'Valor promedio',
        'media_acumulada_concatenada.png',
        num_corridas, tiradas_por_corrida,
    )


def graficar_varianza_acumulada_concatenada(varianza_concat, num_corridas, tiradas_por_corrida):
    _graficar_concatenado(
        varianza_concat, VARIANZA_TEORICA,
        'Varianza Acumulada Concatenada',
        'Varianza',
        'varianza_acumulada_concatenada.png',
        num_corridas, tiradas_por_corrida,
    )


def graficar_desvio_acumulada_concatenada(desvio_concat, num_corridas, tiradas_por_corrida):
    _graficar_concatenado(
        desvio_concat, DESVIO_TEORICO,
        'Desvío Estándar Acumulado Concatenado',
        'Desvío estándar',
        'desvio_acumulada_concatenada.png',
        num_corridas, tiradas_por_corrida,
    )
