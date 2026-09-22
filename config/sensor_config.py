"""Configuration constants for gas sensors and system updates."""

SENSOR_ORDER = ["mics5524", "tgs2600", "mq2", "mq135"]

SENSOR_CONFIG = {
    "mics5524": {
        "name": "MICS-5524",
        "unit": "V",
        "min": 0.0,
        "max": 5.0,
        "warning": 2.0,
        "danger": 3.0,
        "channel": 0
    },
    "tgs2600": {
        "name": "TGS2600",
        "unit": "V",
        "min": 0.0,
        "max": 5.0,
        "warning": 2.0,
        "danger": 3.0,
        "channel": 1
    },
    "mq2": {
        "name": "MQ-2",
        "unit": "V",
        "min": 0.0,
        "max": 5.0,
        "warning": 2.0,
        "danger": 3.0,
        "channel": 2
    },
    "mq135": {
        "name": "MQ-135",
        "unit": "V",
        "min": 0.0,
        "max": 5.0,
        "warning": 2.0,
        "danger": 3.0,
        "channel": 3
    }
}

GAS_ORDER = ["CO", "LPG/Propana", "NH3", "Benzena", "Hidrogen", "Metana", "Asap", "CO2"]

SENSOR_GAS_MATRIX = {
    "mics5524": ["CO"],
    "tgs2600": ["LPG/Propana"],
    "mq2": ["Asap", "Metana", "Hidrogen"],
    "mq135": ["NH3", "Benzena", "CO2"]
}

SENSOR_UPDATE_MS = 1000
CLOCK_UPDATE_MS = 1000
STATUS_UPDATE_MS = 1000
