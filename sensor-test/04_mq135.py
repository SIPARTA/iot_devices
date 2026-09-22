import time
import board

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15


i2c = board.I2C()
ads = ADS1115(i2c)

sensor = AnalogIn(ads, ads1x15.Pin.A3)

print("=" * 55)
print("                MQ-135 SENSOR")
print("=" * 55)
print("MQ-135 OUT -> ADS1115 A3")
print("Membaca ADC dan Voltage")
print("Tekan CTRL+C untuk berhenti")
print("=" * 55)

while True:
    print(
        f"ADC     : {sensor.value:5d} | "
        f"Voltage : {sensor.voltage:.3f} V"
    )

    time.sleep(1)
