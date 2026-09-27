import time
import board

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

i2c = board.I2C()

ads = ADS1115(i2c)

chan_a0 = AnalogIn(ads, ads1x15.Pin.A0)
chan_a1 = AnalogIn(ads, ads1x15.Pin.A1)
chan_a2 = AnalogIn(ads, ads1x15.Pin.A2)
chan_a3 = AnalogIn(ads, ads1x15.Pin.A3)

print("=" * 55)
print("                 ADS1115 TEST")
print("=" * 55)
print("Membaca A0, A1, A2 dan A3")
print("Tekan CTRL+C untuk berhenti")
print("=" * 55)


while True:

    print(
        f"A0 : {chan_a0.value:5d} | "
        f"{chan_a0.voltage:.3f} V"
    )

    print(
        f"A1 : {chan_a1.value:5d} | "
        f"{chan_a1.voltage:.3f} V"
    )

    print(
        f"A2 : {chan_a2.value:5d} | "
        f"{chan_a2.voltage:.3f} V"
    )

    print(
        f"A3 : {chan_a3.value:5d} | "
        f"{chan_a3.voltage:.3f} V"
    )

    print("-" * 55)

    time.sleep(1)