import pandas as pd
import numpy as np

def leer_receptor_phyphox(ruta_archivo_excel):
    df = pd.read_excel(ruta_archivo_excel)
    
    tiempo = df['Time (s)'].values
    luminancia = df['Luminance'].values
    
    umbral = (np.max(luminancia) + np.min(luminancia)) / 2
    bits_recibidos = [1 if l > umbral else 0 for l in luminancia]
    
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

def procesar_transmision(ruta_excel):
    bits_totales = leer_receptor_phyphox(ruta_excel)
    
    preambulo = [1, 0, 1, 0]
    
    indice_inicio = -1
    for i in range(len(bits_totales) - len(preambulo) + 1):
        if bits_totales[i:i+len(preambulo)] == preambulo:
            indice_inicio = i + len(preambulo)
            break
            
    if indice_inicio == -1:
        print("No se encontró el preámbulo de sincronización.")
        return
        
    bits_datos = bits_totales[indice_inicio:]
    
    bits_limpios = []
    for i in range(0, len(bits_datos) - 6, 7):
        bloque_7 = list(bits_datos[i:i+7])
        if len(bloque_7) < 7:
            break
        bits_limpios.extend(decodificar_hamming_74(bloque_7))
        
    mensaje = bits_a_texto(bits_limpios)
    print(f"Frase: {mensaje}")

if __name__ == "__main__":
    archivo = "nombre_excel_phyphox.xlsx"
    procesar_transmision(archivo)