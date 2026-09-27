# SIPARTA IoT Devices (Local UI)

Direktori ini menampung aplikasi GUI (Graphical User Interface) lokal berbasis **PyQt5** yang dirancang untuk ditampilkan langsung pada layar eksternal yang menempel pada Raspberry Pi.

## 1. Project Overview

Awalnya, modul ini bertugas untuk membaca sensor gas secara mandiri, berinteraksi langsung ke jaringan blockchain, serta memutar suara bel darurat. UI ini dikembangkan menggunakan PyQt5 dan Python 3.

Namun, untuk alasan optimasi dan pembagian beban asinkron, **logika utama komunikasi backend telah dipindahkan ke modul `ai_models/main_rpi.py`**. Modul `iot-devices` saat ini murni berfungsi sebagai layer visualisasi luring (offline) bagi operator yang berada langsung di lokasi perangkat (Layar LCD 7-inch Raspberry Pi).

## 2. Architecture Overview

- **Framework**: PyQt5
- **Modules**:
  - `ui/`: Menyimpan semua *View* (layar utama, panel sensor, histori).
  - `core/`: Skrip utilitas pembacaan sensor dan deteksi lokal untuk UI.
  - `scripts/`: Skrip uji coba sensor.

## 3. Prerequisites

Jika Anda ingin menjalankan GUI ini di Raspberry Pi, pastikan lingkungan X11 / Wayland Desktop (Raspberry Pi OS with Desktop) telah menyala, dan Anda memiliki instalasi PyQt5:
```bash
sudo apt-get install python3-pyqt5
```

## 4. Running the Application

Masuk ke dalam direktori ini dan eksekusi file utama UI:
```bash
python ui/main_window.py
```
*(Catatan: Anda mungkin memerlukan layar terhubung via HDMI/DSI atau meneruskan tampilan via VNC/X11 Forwarding)*

## 5. Integration Notice (Penting!)

> [!WARNING]
> Aplikasi GUI ini **TIDAK** lagi mengirimkan request POST secara mandiri ke FastAPI `web-backend` ataupun menjalankan skrip Blockchain Relay di latar belakang.
> Semua alur transmisi data asinkron (*End-to-End*) sekarang ditangani secara terpusat oleh skrip `main_rpi.py` di dalam direktori `ai_models/`. 
> 
> Mohon baca [README.md di direktori ai_models](../ai_models/README.md) untuk setup komunikasi data perangkat IoT Anda ke server SIPARTA.

## 6. Troubleshooting

- **Symptom**: Error `qt.qpa.xcb: could not connect to display` saat menjalankan skrip Python.
  - **Penyebab**: Anda mengeksekusi skrip PyQt5 melalui SSH tanpa dukungan display (*Headless*).
  - **Solusi**: Hubungkan monitor ke Raspberry Pi, atau jalankan perintah dengan environment variable `export DISPLAY=:0`, atau gunakan VNC.
