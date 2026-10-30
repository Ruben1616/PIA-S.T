import time
import numpy as np
import screen_brightness_control as sbc

print("Iniciando script...", flush=True)

def texto_a_bits(texto):
    bits_mensaje = []
    for c in texto:
        binario = format(ord(c), '08b')
        for b in binario:
            bits_mensaje.append(int(b))
    return bits_mensaje

def codificar_hamming_74(bloque_4bits):
    d1, d2, d3, d4 = bloque_4bits
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p3, d2, d3, d4]

def calcular_ber(bits_enviados, bits_recibidos):
    errores = sum(e != r for e, r in zip(bits_enviados, bits_recibidos))
    return errores / len(bits_enviados)

def transmitir_trama():
    mensaje = "facultad de ciencias fisico mate"
    bits_puros = texto_a_bits(mensaje)
    
    trama_hamming = []
    preambulo = [1, 0, 1, 0]
    
    for i in range(0, len(bits_puros), 4):
        bloque = bits_puros[i:i+4]
        trama_hamming.extend(codificar_hamming_74(bloque))
    
    trama_completa = preambulo + trama_hamming
    
    print(f">>> Trama total con Hamming(7,4) generada: {len(trama_completa)} bits", flush=True)
    print("Prepara tu teléfono para capturar la transmisión...", flush=True)
    
    time.sleep(2)
    for idx, bit in enumerate(trama_completa):
        try:
            if bit == 1:
                sbc.set_brightness(100)
            else:
                sbc.set_brightness(0)
        except Exception as e:
            print(f"Error al cambiar brillo en bit {idx}: {e}", flush=True)
        time.sleep(0.5)
        
    sbc.set_brightness(50)
    print("Fin de la transmisión.", flush=True)
    
    tasa_ruido = 0.05
    bits_recibidos_con_ruido = [
        (1 - b) if np.random.rand() < tasa_ruido else b 
        for b in trama_completa
    ]
    
    ber_obtenida = calcular_ber(trama_completa, bits_recibidos_con_ruido)
    print(f"\n--- REPORTE DE BER ---", flush=True)
    print(f"BER estimada con ruido del {tasa_ruido*100}%: {ber_obtenida:.4f}", flush=True)

if __name__ == "__main__":
    transmitir_trama()