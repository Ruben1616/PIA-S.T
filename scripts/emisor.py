#nuevo emisor de mensaje
import time

import numpy as np
import screen_brightness_control as sbc


DURACION_BIT = 1.5  # Segundos por bit; modifica este valor si lo necesitas.


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
    mensaje = "transmisiones guillermo"
    bits_puros = texto_a_bits(mensaje)

    trama_hamming = []
    preambulo = [1, 0, 1, 0]
    for i in range(0, len(bits_puros), 4):
        bloque = bits_puros[i:i + 4]
        trama_hamming.extend(codificar_hamming_74(bloque))
    trama_completa = preambulo + trama_hamming

    print(f">>> Trama total con Hamming(7,4) generada: {len(trama_completa)} bits", flush=True)
    print(f">>> Duración nominal: {len(trama_completa) * DURACION_BIT:.2f} segundos", flush=True)
    print("Prepara tu teléfono para capturar la transmisión...", flush=True)
    print(trama_completa)
    time.sleep(5)

    bit_anterior = None
    for idx, bit in enumerate(trama_completa):
        if bit != bit_anterior:
            try:
                sbc.set_brightness(100 if bit == 1 else 0)
                bit_anterior = bit
            except Exception as e:
                print(f"Error al cambiar brillo en bit {idx}: {e}", flush=True)
        time.sleep(DURACION_BIT)

    sbc.set_brightness(35)
    print("Fin de la transmisión.", flush=True)

    # El BER de la trama se calcula antes de corregir/decodificar Hamming.
    tasa_ruido = 0.05
    bits_puros_con_ruido = [
        (1 - b) if np.random.rand() < tasa_ruido else b
        for b in bits_puros
    ]
    ber_sin_codigo = calcular_ber(bits_puros, bits_puros_con_ruido)

    trama_con_ruido = [
        (1 - b) if np.random.rand() < tasa_ruido else b
        for b in trama_completa
    ]
    ber_con_codigo = calcular_ber(trama_completa, trama_con_ruido)

    print(f"\n--- REPORTE DE BER SIMULADO (Ruido inyectado: {tasa_ruido * 100}%) ---", flush=True)
    print(f"BER SIN código Hamming: {ber_sin_codigo:.4f}", flush=True)
    print(f"BER de trama Hamming ANTES de corregir: {ber_con_codigo:.4f}", flush=True)


if __name__ == "__main__":
    transmitir_trama()
