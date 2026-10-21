


import time
import screen_brightness_control as sbc
#conversion de decimal a binario
def texto_a_bits(texto):
    preambulo = [1, 0 ,1, 0]
    bits_mensaje = []
    for c in texto:
        binario = format(ord(c), '08b')
        for b in binario:
            bits_mensaje.append(int(b))
    return preambulo + bits_mensaje


def transmitir_trama():
    mensaje = "facultad de ciencias fisico mate"
    trama = texto_a_bits(mensaje)
    print("Trama a transmitir:", trama)
    print("prepara tu telefono, hay 4 bits de preambulo")
    
    time.sleep(2)
    for bit in trama:
        if bit == 1:
            sbc.set_brightness(100)
        else:
            sbc.set_brightness(0)
        time.sleep(0.5)
    sbc.set_brightness(50)
    print("Fin de la transmision")

if __name__ == "__main__":
    transmitir_trama()