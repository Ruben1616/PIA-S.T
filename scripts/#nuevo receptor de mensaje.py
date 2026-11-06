#nuevo receptor de mensaje
"""Recupera bits de un Excel de phyphox usando tiempo, cantidad y umbral.

Instalar: python -m pip install openpyxl
Ejecutar: python decodificador_excel_umbral.py
La luminancia promedio del centro del intervalo determina cada bit.
El Excel usa la primera hoja, con encabezados en la fila 1, tiempo en A y luminancia en C.
"""
from bisect import bisect_left
from pathlib import Path
from statistics import mean
import sys

from openpyxl import load_workbook

# Tiempo previsto en el transmisor. El receptor calcula su propio promedio.
DURACION_NOMINAL = 1.5


def numero(valor):
    """Lee un número y permite usar punto o coma decimal."""
    return float(str(valor).replace(',', '.'))


def leer_excel(ruta):
    """Lee el tiempo de A y la luminancia de C en la primera hoja."""
    # Abre el archivo para leer los valores guardados en las celdas.
    libro = load_workbook(ruta, read_only=True, data_only=True, keep_links=False)
    try:
        hoja = libro.worksheets[0]
        filas = hoja.iter_rows(min_row=1, max_col=3, values_only=True)
        # next consume la primera fila, que contiene los encabezados.
        next(filas)
        # Cada muestra se guarda como (tiempo, luminancia). El _ ignora la columna B.
        datos = [(numero(tiempo), numero(luz)) for tiempo, _, luz in filas]
    finally:
        libro.close()
    return datos


def decodificar(datos, inicio, fin, total_bits, umbral):
    """Calcula la duración promedio y lee exactamente la cantidad de bits indicada."""
    # Entre el inicio del primer bit y el fin del último caben todos los bits.
    duracion = (fin - inicio) / total_bits
    # Ordenar por tiempo permite buscar las muestras de cada intervalo.
    datos = sorted(datos)
    tiempos = [t for t, _ in datos]
    bits = []
    for i in range(total_bits):
        # Coloca cada bit en un intervalo con la misma duración promedio.
        desde = inicio + i * duracion
        # Usa del 25 % al 75 % del intervalo para alejarse de los cambios de brillo.
        centro_inicio = desde + duracion * 0.25
        centro_fin = desde + duracion * 0.75
        # bisect_left localiza el primer dato en cada límite de la zona de lectura.
        izquierda = bisect_left(tiempos, centro_inicio)
        derecha = bisect_left(tiempos, centro_fin)
        muestras = datos[izquierda:derecha]
        # El promedio se compara con el umbral. Un ? indica que faltan muestras.
        promedio = mean(valor for _, valor in muestras) if muestras else None
        bit = '?'
        if promedio is not None:
            bit = '1' if promedio >= umbral else '0'
        bits.append(bit)
    return ''.join(bits), duracion


def recuperar_mensaje(bits):
    """Retira los cuatro bits de preámbulo y aplica Hamming al resto."""
    # Los primeros cuatro bits corresponden al preámbulo del transmisor.
    carga = bits[4:]
    bloques_datos, correcciones = [], 0
    for i in range(0, len(carga), 7):
        # Cada bloque Hamming contiene cuatro bits de datos y tres de paridad.
        bloque = list(map(int, carga[i:i + 7]))
        p1, p2, d1, p3, d2, d3, d4 = bloque
        # El operador ^ comprueba cada paridad. Los tres resultados señalan
        # la posición que se debe invertir si el bloque tiene un solo error.
        s1 = p1 ^ d1 ^ d2 ^ d4
        s2 = p2 ^ d1 ^ d3 ^ d4
        s3 = p3 ^ d2 ^ d3 ^ d4
        posicion = s1 + 2 * s2 + 4 * s3
        # Una posición de 0 indica que las tres paridades coinciden.
        if posicion:
            bloque[posicion - 1] ^= 1
            correcciones += 1
        # Extrae los bits de datos en las posiciones 3, 5, 6 y 7 del bloque.
        bloques_datos.extend(str(bloque[j]) for j in (2, 4, 5, 6))
    # Cada ocho bits forman un byte. Latin-1 conserva el valor de ocho bits
    # por carácter que usa el transmisor, por ejemplo en la letra ñ.
    datos = ''.join(bloques_datos)
    mensaje = bytes(int(datos[i:i + 8], 2) for i in range(0, len(datos), 8)).decode('latin-1')
    return mensaje, correcciones


def guardar_mensaje(mensaje):
    """Guarda el texto recuperado en la carpeta desde la que se ejecuta el programa."""
    base = Path.cwd() / 'mensaje_decodificado.txt'
    archivo, copia = base, 2
    while True:
        try:
            # El modo x crea el archivo solo si el nombre está libre.
            with archivo.open('x', encoding='utf-8') as salida:
                salida.write(mensaje)
            return archivo
        except FileExistsError:
            archivo = base.with_name(f'{base.stem}_{copia}{base.suffix}')
            copia += 1


def main():
    """Solicita los datos de la captura y muestra la secuencia recuperada."""
    # La ruta se puede escribir al ejecutar el programa o cuando se solicita.
    archivo = sys.argv[1] if len(sys.argv) > 1 else input('Ruta del archivo .xlsx: ')
    ruta = Path(archivo.strip().strip('"'))
    datos = leer_excel(ruta)
    print(f'Muestras leídas: {len(datos)}.')
    # Estos datos sirven para ubicar los intervalos y clasificar la luminancia.
    total = int(input('Cantidad total de bits enviados, incluido el preámbulo: '))
    inicio = numero(input('Segundo de INICIO del primer bit: '))
    fin = numero(input('Segundo de FIN del último bit recibido: '))
    umbral = numero(input('Umbral de luminancia (valor igual o mayor = bit 1): '))
    bits, duracion = decodificar(datos, inicio, fin, total, umbral)
    print(f'\nDuración nominal: {DURACION_NOMINAL} s. Promedio calculado: {duracion:.6f} s.')
    print('Bits recuperados:', bits)
    print(f'Total: {len(bits)}. Sin muestras en el centro (?): {bits.count("?")}.')
    # Guarda el archivo solo después de reconstruir el texto.
    try:
        mensaje, correcciones = recuperar_mensaje(bits)
    except ValueError as error:
        print('No se pudo recuperar el texto:', error)
    else:
        print('Mensaje recuperado:', mensaje)
        print(f'Bloques Hamming con corrección aplicada: {correcciones}')
        archivo = guardar_mensaje(mensaje)
        print('Mensaje guardado en:', archivo.resolve())


# Inicia las preguntas al ejecutar este archivo como programa.
if __name__ == '__main__':
    main()
