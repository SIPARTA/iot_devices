import time
import math
import board

from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15


# ============================================================
# KONFIGURASI MQ-2
# ============================================================

VC = 5.0
RL = 2000.0

# SEMENTARA
# Nanti sebaiknya diganti dengan RO hasil kalibrasi.
RO = 45918.3


# ============================================================
# SETUP ADS1115
# ============================================================

i2c = board.I2C()

ads = ADS1115(i2c)

mq2 = AnalogIn(
    ads,
    ads1x15.Pin.A2
)


# ============================================================
# ESTIMASI LPG
# ============================================================

def estimate_lpg_ppm(rs, ro):

    if rs <= 0 or ro <= 0:
        return 0.0

    ratio = rs / ro

    if ratio <= 0:
        return 0.0

    # --------------------------------------------------------
    # Pendekatan kurva LPG MQ-2
    #
    # log10(Rs/Ro) = m * log10(PPM) + b
    #
    # sehingga:
    #
    # PPM = 10 ^ ((log10(Rs/Ro) - b) / m)
    # --------------------------------------------------------

    m = -0.47
    b = 1.28

    try:

        log_ratio = math.log10(ratio)

        log_ppm = (
            (log_ratio - b) / m
        )

        ppm = math.pow(
            10,
            log_ppm
        )

    except (ValueError, OverflowError):

        return 0.0


    # --------------------------------------------------------
    # Batasi ke rentang MQ-2 yang kita gunakan
    # --------------------------------------------------------

    if ppm < 300:

        ppm = 0.0

    elif ppm > 10000:

        ppm = 10000.0


    return ppm


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("                    MQ-2 LPG MONITOR")
print("=" * 75)

print("Sensor      : MQ-2")
print("ADC Channel : ADS1115 A2")
print(f"VC          : {VC:.2f} V")
print(f"RL          : {RL:.0f} Ohm")
print(f"RO          : {RO:.1f} Ohm")

print("=" * 75)
print("LPG = ESTIMATED VALUE")
print("Range model : 300 - 10000 ppm")
print("=" * 75)


# ============================================================
# LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # ADC
    # --------------------------------------------------------

    adc_value = mq2.value


    # --------------------------------------------------------
    # VOUT
    # --------------------------------------------------------

    vout = mq2.voltage


    # --------------------------------------------------------
    # Rs
    # --------------------------------------------------------

    if 0 < vout < VC:

        rs = RL * (
            (VC - vout) / vout
        )

    else:

        rs = 0.0


    # --------------------------------------------------------
    # Rs/Ro
    # --------------------------------------------------------

    if RO > 0 and rs > 0:

        ratio = rs / RO

    else:

        ratio = 0.0


    # --------------------------------------------------------
    # LPG PPM
    # --------------------------------------------------------

    lpg_ppm = estimate_lpg_ppm(
        rs,
        RO
    )


    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print(
        f"ADC: {adc_value:5d} | "
        f"VOUT: {vout:.3f} V | "
        f"Rs: {rs:9.1f} Ohm | "
        f"Rs/Ro: {ratio:.3f} | "
        f"LPG: {lpg_ppm:7.1f} ppm EST."
    )


    time.sleep(1)
