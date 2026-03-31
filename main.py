from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from predict_nutrient import predict_nutrients
from download_model import download_model
import os
import requests

app = FastAPI()

# -----------------------------
# Load model (download if needed)
# -----------------------------
download_model()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# HuggingFace AI
# -----------------------------
HF_TOKEN = os.getenv("HF_TOKEN")  # 🔥 secure way

def generate_ai_recommendation(nutrition, goal, disease, age, gender):
    prompt = f"""
You are a professional nutritionist AI.

User:
Age: {age}
Gender: {gender}
Goal: {goal}
Disease: {disease}

Nutrition:
Calories: {nutrition['calories']}
Protein: {nutrition['protein']}
Carbohydrates: {nutrition['carbohydrates']}
Fats: {nutrition['fats']}
Fiber: {nutrition['fiber']}
Sugars: {nutrition['sugars']}
Sodium: {nutrition['sodium']}

Give:
1. Health verdict
2. Reason
3. 3 suggestions
"""

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt},
            timeout=30
        )

        data = response.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "No response")

        return "AI unavailable"

    except Exception as e:
        return f"AI Error: {str(e)}"


# -----------------------------
# Predict endpoint
# -----------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...), weight: float = Form(...)):
    try:
        file_location = f"temp_{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())

        result = predict_nutrients(file_location, weight)

        if os.path.exists(file_location):
            os.remove(file_location)

        return result

    except Exception as e:
        return {"error": str(e), "status": "failed"}


# -----------------------------
# Recommend endpoint
# -----------------------------
@app.post("/recommend")
async def recommend(
    calories: float = Form(...),
    protein: float = Form(...),
    carbohydrates: float = Form(...),
    fats: float = Form(...),
    fiber: float = Form(...),
    sugars: float = Form(...),
    sodium: float = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    goal: str = Form(...),
    disease: str = Form("")
):
    try:
        nutrition = {
            "calories": calories,
            "protein": protein,
            "carbohydrates": carbohydrates,
            "fats": fats,
            "fiber": fiber,
            "sugars": sugars,
            "sodium": sodium
        }

        ai_response = generate_ai_recommendation(
            nutrition, goal, disease, age, gender
        )

        return {
            "recommendations": [ai_response],
            "status": "success"
        }

    except Exception as e:
        return {"error": str(e), "status": "failed"}


# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def home():
    return {"message": "Nutrition AI Running 🚀"}
