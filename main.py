


# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# from predict_nutrient import predict_nutrients
# from download_model import download_model
# import os
# import uvicorn
# import google.generativeai as genai

# app = FastAPI()

# # -------------------------
# # CORS
# # -------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------------------
# # RUN MODEL ON STARTUP (FIX)
# # -------------------------
# @app.on_event("startup")
# def load_model():
#     print("Downloading/loading model...")
#     download_model()
#     print("Model ready ✔")

# # -------------------------
# # GEMINI
# # -------------------------
# API_KEY = os.getenv("GEMINI_API_KEY")

# if not API_KEY:
#     print("WARNING: GEMINI_API_KEY not set!")

# genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel("gemini-2.5-flash")


# # -------------------------
# # PREDICT
# # -------------------------
# @app.post("/predict")
# async def predict(file: UploadFile = File(...), weight: float = Form(...)):

#     file_location = f"temp_{file.filename}"

#     with open(file_location, "wb") as f:
#         f.write(await file.read())

#     result = predict_nutrients(file_location, weight)

#     if os.path.exists(file_location):
#         os.remove(file_location)

#     return result


# # -------------------------
# # RECOMMEND
# # -------------------------
# @app.post("/recommend")
# async def recommend(
#     calories: float = Form(...),
#     protein: float = Form(...),
#     carbohydrates: float = Form(...),
#     fats: float = Form(...),
#     fiber: float = Form(...),
#     sugars: float = Form(...),
#     sodium: float = Form(...),
#     age: int = Form(0),
#     gender: str = Form("Unknown"),
#     goal: str = Form("maintain"),
#     disease: str = Form("")
# ):

#     prompt = f"""
# You are a nutrition AI.

# Age: {age}
# Gender: {gender}
# Goal: {goal}
# Disease: {disease}

# Calories: {calories}
# Protein: {protein}
# Carbs: {carbohydrates}
# Fats: {fats}
# Fiber: {fiber}
# Sugar: {sugars}
# Sodium: {sodium}

# Give 4-6 line advice.
# """

#     response = model.generate_content(prompt)

#     return {
#         "recommendations": [response.text]
#     }


# # -------------------------
# # RUN
# # -------------------------
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from predict_nutrient import predict_nutrients
from download_model import download_model
import os
import requests

app = FastAPI()

# -----------------------------
# Model load
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
# 🔥 FREE AI (HuggingFace)
# -----------------------------
HF_TOKEN = "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"

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

    response = requests.post(
        "https://api-inference.huggingface.co/models/google/flan-t5-base",
        headers={
            "Authorization": f"Bearer {HF_TOKEN}"
        },
        json={
            "inputs": prompt
        }
    )

    try:
        return response.json()[0]["generated_text"]
    except:
        return "AI is loading or unavailable. Try again."


# -----------------------------
# Predict endpoint
# -----------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...), weight: float = Form(...)):
    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as f:
        f.write(await file.read())

    result = predict_nutrients(file_location, weight)

    if os.path.exists(file_location):
        os.remove(file_location)

    return result


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
            nutrition,
            goal,
            disease,
            age,
            gender
        )

        return {
            "recommendations": [ai_response],
            "status": "success"
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }


# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def home():
    return {"message": "Nutrition AI Running 🚀"}












