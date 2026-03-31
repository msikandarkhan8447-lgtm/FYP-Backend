from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from predict_nutrient import predict_nutrients
from download_model import download_model
import os

app = FastAPI()

# Download model if not exists
download_model()

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...), weight: float = Form(...)):
    temp_file = f"temp_{file.filename}"
    
    with open(temp_file, "wb") as f:
        f.write(await file.read())

    result = predict_nutrients(temp_file, weight)

    if os.path.exists(temp_file):
        os.remove(temp_file)

    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
