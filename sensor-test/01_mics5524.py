import time
import math
import board

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15


# ============================================================
# KONFIGURASI MiCS-5524
# ============================================================

VCC = 4.73
RL = 10000.0

# R0 baseline eksperimen
R0 = 396008.6


# ============================================================
# SETUP ADS1115
# ============================================================

i2c = board.I2C()

ads = ADS1115(i2c)

mics5524 = AnalogIn(
    ads,
    ads1x15.Pin.A0
)


# ============================================================
# ESTIMASI CO
# ============================================================

def estimate_co_ppm(rs, r0):

    if rs <= 0 or r0 <= 0:
        return 0.0

    ratio = rs / r0

    try:
        ppm = 3.5 * math.pow(ratio, -0.85)

    except (ValueError, OverflowError):
        return 0.0

    # Batasi sesuai rentang yang sedang kita gunakan
    if ppm < 1.0:
        ppm = 0.0

    elif ppm > 1000.0:
        ppm = 1000.0

    return ppm


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("                 MiCS-5524 CO MONITOR")
print("=" * 75)

print("Sensor      : MiCS-5524")
print("ADC Channel : ADS1115 A0")
print(f"VCC         : {VCC:.2f} V")
print(f"RL          : {RL:.0f} Ohm")
print(f"R0          : {R0:.1f} Ohm")

print("=" * 75)
print("CO = ESTIMATED VALUE")
print("=" * 75)


# ============================================================
# LOOP
# ============================================================

while True:

    # ADC
    adc_value = mics5524.value

    # Tegangan output
    vout = mics5524.voltage

    # --------------------------------------------------------
    # Hitung Rs
    # --------------------------------------------------------

    if 0 < vout < VCC:

        rs = RL * (
            (VCC - vout) / vout
        )

    else:

        rs = 0.0


    # --------------------------------------------------------
    # Hitung Rs/R0
    # --------------------------------------------------------

    if rs > 0:

        ratio = rs / R0

    else:

        ratio = 0.0


    # --------------------------------------------------------
    # Estimasi CO
    # --------------------------------------------------------

    co_ppm = estimate_co_ppm(
        rs,
        R0
    )


    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print(
        f"ADC: {adc_value:5d} | "
        f"VOUT: {vout:.3f} V | "
        f"Rs: {rs:9.1f} Ohm | "
        f"Rs/R0: {ratio:.3f} | "
        f"CO: {co_ppm:6.1f} ppm EST."
    )

    time.sleep(1)