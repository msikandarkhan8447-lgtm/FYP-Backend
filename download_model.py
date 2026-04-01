# import os
# import gdown

# MODEL_PATH = "models/nutrifoodnet_final.h5"
# MODEL_DIR = "models"

# # 🔥 DIRECT DOWNLOAD URL (NOT /view)
# GDRIVE_FILE_ID = "1ho8wwkADHIVGj1Iq5614A3h7uqbhkrTC"
# DOWNLOAD_URL = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"

# def download_model():
#     os.makedirs(MODEL_DIR, exist_ok=True)

#     if os.path.exists(MODEL_PATH):
#         print("✅ Model already exists")
#         return

#     print("📥 Downloading model from Google Drive...")
#     gdown.download(DOWNLOAD_URL, MODEL_PATH, quiet=False)

#     if not os.path.exists(MODEL_PATH):
#         raise RuntimeError("❌ Model download failed")

#     print("✅ Model downloaded successfully")

import os
import requests

MODEL_PATH = "models/nutrifoodnet_final.h5"
MODEL_DIR = "models"

DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id=1ho8wwkADHIVGj1Iq5614A3h7uqbhkrTC"


def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if os.path.exists(MODEL_PATH):
        print("✅ Model already exists")
        return

    print("📥 Downloading model...")

    response = requests.get(DOWNLOAD_URL, stream=True)

    if response.status_code != 200:
        raise RuntimeError("❌ Failed to download model")

    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    if not os.path.exists(MODEL_PATH):
        raise RuntimeError("❌ Model not saved")

    print("✅ Model downloaded successfully")
