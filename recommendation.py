def calculate_bmr(weight, height, age, gender):
    gender = gender.lower()
    if gender in ["male", "m"]:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr


def adjust_calories(bmr, goal):
    goal = goal.lower()

    if goal == "weight_loss":
        return bmr - 500
    elif goal == "weight_gain":
        return bmr + 500
    elif goal == "muscle_gain":
        return bmr + 300
    else:
        return bmr


def generate_recommendation(food_label, nutrition, daily_calories, goal):
    calories = nutrition.get("calories", 0)

    message = ""

    if goal == "weight_loss":
        if calories > 400:
            message = f"{food_label} is high in calories. Try smaller portions or choose grilled/boiled alternatives."
        else:
            message = f"{food_label} is suitable for weight loss in moderate portions."

    elif goal == "weight_gain":
        message = f"{food_label} can help increase calorie intake. Pair it with protein-rich foods."

    elif goal == "muscle_gain":
        protein = nutrition.get("protein", 0)
        if protein < 15:
            message = f"{food_label} is low in protein. Add eggs, chicken, or yogurt."
        else:
            message = f"{food_label} is good for muscle building."

    else:
        message = f"{food_label} can be part of a balanced diet."

    return {
        "daily_calories_target": round(daily_calories, 2),
        "advice": message
    }
