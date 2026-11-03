import pandas as pd
import numpy as np

def leer_receptor_phyphox(ruta_archivo_excel):
    df = pd.read_excel(ruta_archivo_excel)
    
    tiempo = df['Time (s)'].values
    luminancia = df['Luminance'].values
    
    umbral = (np.max(luminancia) + np.min(luminancia)) / 2
    bits_recibidos = [1 if l > umbral else 0 for l in luminancia]
    
    print(f"Total de muestras leídas del archivo: {len(bits_recibidos)}")
    return bits_recibidos

def decodificar_hamming_74(bloque_7bits):
    p1, p2, d1, p3, d2, d3, d4 = bloque_7bits
    
    s1 = p1 ^ d1 ^ d2 ^ d4
    s2 = p2 ^ d1 ^ d3 ^ d4
    s3 = p3 ^ d2 ^ d3 ^ d4
    
    sindrom = s3 * 4 + s2 * 2 + s1
    
    if sindrom > 0 and sindrom <= 7:
        bloque_7bits[sindrom - 1] ^= 1
        
    return [bloque_7bits[2], bloque_7bits[4], bloque_7bits[5], bloque_7bits[6]]

def bits_a_texto(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        val = int("".join(map(str, byte)), 2)
        chars.append(chr(val))
    return "".join(chars)