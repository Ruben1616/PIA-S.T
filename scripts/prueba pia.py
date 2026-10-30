import time as t
import screen_brightness_control as sbc

def transmitir():
    t.sleep(1)
    sbc.set_brightness(100)
    t.sleep(0.5)
    sbc.set_brightness(0)
    t.sleep(0.5)

    sbc.set_brightness(35)
if __name__ == "__main__":
    transmitir()

