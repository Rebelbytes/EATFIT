from flask import Flask, render_template, request, jsonify
from meal import recommend_meal
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def meal_page():
    return render_template("meal.html")

@app.route("/recommend_meal", methods=["POST"])
def get_meal():
    try:
        data = request.get_json()
        age = int(data["age"])
        weight = float(data["weight"])
        height = float(data["height"])
        disease = data["disease"].strip()

        print(f"🔍 User Input -> Age: {age}, Weight: {weight}, Height: {height}, Disease: '{disease}'")

        bmi, bmi_category, breakfast, lunch, dinner = recommend_meal(age, weight, height, disease)

        return jsonify({
            "bmi": round(bmi, 2),
            "bmi_category": bmi_category,
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    if not all(os.path.exists(f) for f in ["rf_breakfast.pkl", "rf_lunch.pkl", "rf_dinner.pkl", "label_encoders.pkl"]):
        print("❌ Model files missing! Ensure .pkl files are in the project folder.")
    else:
        print("✅ All model files are present.")
    app.run(debug=True)
