import time
import math
import board

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

VC = 5.0
RL = 10000.0

RO = 155768.8

i2c = board.I2C()
ads = ADS1115(i2c)

tgs2600 = AnalogIn(
    ads,
    ads1x15.Pin.A1
)

def estimate_h2_ppm(ratio):
    """
    Estimasi H2 berdasarkan karakteristik tipikal TGS2600.

    TGS2600:
    typical detection range = 1–30 ppm H2.

    Hasil adalah ESTIMASI, bukan kalibrasi.
    """

    if ratio <= 0:
        return 0.0


    curve = [
        # (Rs/Ro, ppm H2)
        (1.00, 0.0),
        (0.80, 1.0),
        (0.65, 3.0),
        (0.55, 5.0),
        (0.45, 10.0),
        (0.38, 20.0),
        (0.30, 30.0),
    ]

    # Udara baseline / ratio >= 1
    if ratio >= curve[0][0]:
        return 0.0

    # Di bawah batas curve
    if ratio <= curve[-1][0]:
        return 30.0

    # Cari dua titik yang mengapit ratio
    for i in range(len(curve) - 1):

        r1, ppm1 = curve[i]
        r2, ppm2 = curve[i + 1]

        if r2 <= ratio <= r1:

            # Interpolasi pada skala log ratio
            x1 = math.log10(r1)
            x2 = math.log10(r2)
            x = math.log10(ratio)

            fraction = (x - x1) / (x2 - x1)

            ppm = ppm1 + fraction * (ppm2 - ppm1)

            return ppm

    return 0.0



print("=" * 75)
print("                  TGS2600 AIR MONITOR")
print("=" * 75)

print("Sensor      : TGS2600")
print("ADC Channel : ADS1115 A1")
print(f"VC          : {VC:.2f} V")
print(f"RL          : {RL:.0f} Ohm")
print(f"RO          : {RO:.1f} Ohm")

print("=" * 75)
print("H2 = ESTIMATED VALUE")
print("Typical detection range: 1-30 ppm H2")
print("=" * 75)



while True:

    adc_value = tgs2600.value

    vout = tgs2600.voltage



    if 0 < vout < VC:

        rs = RL * (
            (VC - vout) / vout
        )

    else:

        rs = 0.0



    if RO > 0 and rs > 0:

        ratio = rs / RO

    else:

        ratio = 0.0

    h2_ppm = estimate_h2_ppm(ratio)



    print(
        f"ADC: {adc_value:5d} | "
        f"VOUT: {vout:.3f} V | "
        f"Rs: {rs:9.1f} Ohm | "
        f"Rs/Ro: {ratio:.3f} | "
        f"H2: {h2_ppm:5.1f} ppm EST."
    )

    time.sleep(1)
