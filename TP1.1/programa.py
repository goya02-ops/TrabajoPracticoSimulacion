import argparse
from motor import iniciar_experimento
from CONSTANTES import MEDIA_TEORICA
import statistics
from graficos import (
    graficar_histograma,
    graficar_distribucion_medias,
    graficar_boxplot_medias,
    graficar_frecuencia_relativa_concatenada,
    graficar_frecuencia_relativa_multiples,
    graficar_media_acumulada_concatenada,
    graficar_varianza_acumulada_concatenada,
    graficar_desvio_acumulada_concatenada,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Simulación de Ruleta Europea')
    parser.add_argument('-c', '--tiradas', type=int, default=10000,
                        help='Cantidad de tiradas por corrida')
    parser.add_argument('-n', '--corridas', type=int, default=200,
                        help='Cantidad de corridas para la distribución de medias')
    parser.add_argument('-e', '--elegido', type=int, default=18,
                        help='Número elegido para análisis')
    return parser.parse_args()


def main():
    args = parse_arguments()
    cantidad_tiradas = args.tiradas
    numero_elegido = args.elegido
    num_corridas = args.corridas

    resultados = iniciar_experimento(
        num_corridas, cantidad_tiradas, numero_elegido)

    graficar_frecuencia_relativa_concatenada(
        resultados['frec_concat'], numero_elegido, num_corridas, cantidad_tiradas)
    if num_corridas <= 15:
        # Solo graficamos las frecuencias relativas individuales si no hay demasiadas corridas, para evitar saturar el gráfico
        graficar_frecuencia_relativa_multiples(
            resultados['todas_frec'], num_corridas)
    graficar_media_acumulada_concatenada(
        resultados['media_concat'], num_corridas, cantidad_tiradas)
    graficar_varianza_acumulada_concatenada(
        resultados['varianza_concat'], num_corridas, cantidad_tiradas)
    graficar_desvio_acumulada_concatenada(
        resultados['desvio_concat'], num_corridas, cantidad_tiradas)

    graficar_histograma(
        resultados['resultados_concat'], num_corridas, cantidad_tiradas)

    medias = resultados['todas_las_medias']
    if num_corridas >= 200:
        # Solo graficamos la distribución de las medias si hay una cantidad razonable de corridas, para que tenga sentido visualmente
        graficar_distribucion_medias(medias, num_corridas, cantidad_tiradas)
    graficar_boxplot_medias(medias, num_corridas, cantidad_tiradas)

    print(f'Media de las medias: {statistics.mean(medias):.4f}')
    print(f'Desvío estándar de las medias: {statistics.stdev(medias):.4f}')
    print(f'Media teórica: {MEDIA_TEORICA}')


if __name__ == '__main__':
    main()
