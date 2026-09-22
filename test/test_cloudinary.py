"""Simple Cloudinary image upload test.

Usage:
    python scripts/test_cloudinary.py <image_path>

Example:
    python scripts/test_cloudinary.py photo.jpg
    python scripts/test_cloudinary.py /home/pi/sensor_monitor/evidence/test.png
"""

import os
import sys
from pathlib import Path

# load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = val

import cloudinary
import cloudinary.uploader

CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

if not all([CLOUD_NAME, API_KEY, API_SECRET]):
    print("ERROR: Isi CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET di .env")
    sys.exit(1)

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

if len(sys.argv) < 2:
    print("Usage: python test_cloudinary.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]
if not os.path.isfile(image_path):
    print(f"ERROR: File not found — {image_path}")
    sys.exit(1)

print(f"Uploading {image_path} ...")
result = cloudinary.uploader.upload(
    image_path,
    folder="siparta/evidence",
)

print(f"URL        : {result['secure_url']}")
print(f"Public ID  : {result['public_id']}")
print(f"Format     : {result.get('format')}")
print(f"Size       : {result.get('bytes', 0)} bytes")
