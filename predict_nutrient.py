# import tensorflow as tf
# from tensorflow.keras.preprocessing import image
# import numpy as np
# import pandas as pd
# import json
# import os

# # -------------------------------
# # PATHS (Railway-safe)
# # -------------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MODEL_PATH = os.path.join(BASE_DIR, "models", "nutrifoodnet_final.h5")
# CLASS_LABELS_PATH = os.path.join(BASE_DIR, "models", "class_labels.json")
# NUTRITION_CSV = os.path.join(BASE_DIR, "data", "nutrition.csv")

# IMAGE_SIZE = (299, 299)

# # -------------------------------
# # GLOBALS (lazy loaded)
# # -------------------------------
# model = None
# class_labels = None
# nutrition_df = None
# numeric_cols = ["weight","calories","protein","carbohydrates","fats","fiber","sugars","sodium"]

# # -------------------------------
# # LOADERS
# # -------------------------------
# def load_model_once():
#     global model
#     if model is None:
#         if not os.path.exists(MODEL_PATH):
#             raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
#         print("Loading ML model...")
#         model = tf.keras.models.load_model(
#     MODEL_PATH,
#     compile=False
# )
#         print("MODEL LOADED")

# def load_class_labels_once():
#     global class_labels
#     if class_labels is None:
#         with open(CLASS_LABELS_PATH, "r") as f:
#             class_labels = json.load(f)

# def load_nutrition_once():
#     global nutrition_df
#     if nutrition_df is None:
#         nutrition_df = pd.read_csv(NUTRITION_CSV)
#         nutrition_df[numeric_cols] = nutrition_df[numeric_cols].astype(float)

# # -------------------------------
# # PREDICTION FUNCTION
# # -------------------------------
# def predict_nutrients(img_path, target_weight=100):
#     load_model_once()
#     load_class_labels_once()
#     load_nutrition_once()

#     img = image.load_img(img_path, target_size=IMAGE_SIZE)
#     x = image.img_to_array(img)
#     x = np.expand_dims(x, axis=0) / 255.0

#     pred = model.predict(x)
#     pred_class_idx = int(np.argmax(pred))
#     confidence = float(pred[0][pred_class_idx])

#     food_name = class_labels[str(pred_class_idx)]

#     food_rows = nutrition_df[nutrition_df["label"] == food_name]
#     if food_rows.empty:
#         return {"error": "Nutrition info not found"}

#     food_rows = food_rows.reset_index(drop=True)
#     closest_row = food_rows.iloc[(food_rows['weight'] - target_weight).abs().argsort()[0]]

#     result = {
#         "label": food_name,
#         "confidence": round(confidence, 4),
#     }

#     for col in closest_row.index:
#         result[col] = float(closest_row[col]) if col in numeric_cols else closest_row[col]

#     return result




import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import pandas as pd
import json
import os

# -------------------------------
# PATHS (Railway-safe)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "nutrifoodnet_final.h5")
CLASS_LABELS_PATH = os.path.join(BASE_DIR, "models", "class_labels.json")
NUTRITION_CSV = os.path.join(BASE_DIR, "data", "nutrition.csv")

IMAGE_SIZE = (299, 299)

# -------------------------------
# GLOBALS (lazy loaded)
# -------------------------------
model = None
class_labels = None
nutrition_df = None

numeric_cols = [
    "weight",
    "calories",
    "protein",
    "carbohydrates",
    "fats",
    "fiber",
    "sugars",
    "sodium"
]

# -------------------------------
# LOAD MODEL (FIXED)
# -------------------------------
def load_model_once():
    global model

    if model is not None:
        return

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ Model not found at: {MODEL_PATH}")

    try:
        print("🚀 Loading ML model...")
        
        model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False   # 🔥 CRITICAL FIX
        )

        print("✅ MODEL LOADED SUCCESSFULLY")

    except Exception as e:
        print("❌ MODEL LOAD FAILED:", str(e))
        raise e


# -------------------------------
# LOAD CLASS LABELS
# -------------------------------
def load_class_labels_once():
    global class_labels

    if class_labels is not None:
        return

    if not os.path.exists(CLASS_LABELS_PATH):
        raise FileNotFoundError(f"❌ Class labels not found: {CLASS_LABELS_PATH}")

    with open(CLASS_LABELS_PATH, "r") as f:
        class_labels = json.load(f)

    print("✅ Class labels loaded")


# -------------------------------
# LOAD NUTRITION DATA
# -------------------------------
def load_nutrition_once():
    global nutrition_df

    if nutrition_df is not None:
        return

    if not os.path.exists(NUTRITION_CSV):
        raise FileNotFoundError(f"❌ Nutrition CSV not found: {NUTRITION_CSV}")

    nutrition_df = pd.read_csv(NUTRITION_CSV)

    # Ensure numeric columns are float
    for col in numeric_cols:
        if col in nutrition_df.columns:
            nutrition_df[col] = nutrition_df[col].astype(float)

    print("✅ Nutrition data loaded")


# -------------------------------
# IMAGE PREPROCESSING
# -------------------------------
def preprocess_image(img_path):
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"❌ Image not found: {img_path}")

    img = image.load_img(img_path, target_size=IMAGE_SIZE)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0

    return x


# -------------------------------
# MAIN PREDICTION FUNCTION
# -------------------------------
def predict_nutrients(img_path, target_weight=100):
    try:
        # Load everything safely
        load_model_once()
        load_class_labels_once()
        load_nutrition_once()

        # Preprocess image
        x = preprocess_image(img_path)

        # Predict
        pred = model.predict(x)
        pred_class_idx = int(np.argmax(pred))
        confidence = float(pred[0][pred_class_idx])

        # Get label
        food_name = class_labels.get(str(pred_class_idx), "Unknown")

        # Get nutrition data
        food_rows = nutrition_df[nutrition_df["label"] == food_name]

        if food_rows.empty:
            return {
                "label": food_name,
                "confidence": round(confidence, 4),
                "error": "Nutrition info not found"
            }

        food_rows = food_rows.reset_index(drop=True)

        # Find closest weight match
        closest_row = food_rows.iloc[
            (food_rows["weight"] - target_weight).abs().argsort()[0]
        ]

        # Build result
        result = {
            "label": food_name,
            "confidence": round(confidence, 4),
        }

        for col in closest_row.index:
            if col in numeric_cols:
                result[col] = float(closest_row[col])
            else:
                result[col] = closest_row[col]

        return result

    except Exception as e:
        print("❌ Prediction error:", str(e))
        return {
            "error": str(e)
        }
