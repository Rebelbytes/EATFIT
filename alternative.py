import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# Load the dataset
file_path = r"foodpr_cleaned_dataset (3).csv"
df = pd.read_csv(file_path)

# Select relevant columns for analysis (including the image URL)
columns_to_use = ["product_name", "ingredients_text", "nutriscore_score", "nutriscore_grade", 
                  "fat_100g", "energy-kcal_100g", "image_url", "quantity", "labels", "categories"]

# Filter data
data = df[columns_to_use].dropna()

# Encode categorical data (Nutriscore grade)
label_encoder = LabelEncoder()
data['nutriscore_grade'] = label_encoder.fit_transform(data['nutriscore_grade'])

# Normalize numerical data (Nutriscore score, fat, calories)
scaler = StandardScaler()
data[['nutriscore_score', 'fat_100g', 'energy-kcal_100g']] = scaler.fit_transform(data[['nutriscore_score', 'fat_100g', 'energy-kcal_100g']])

# Simulating target labels (BP, Diabetes, Obesity) - Replace with real data
data['condition'] = np.random.choice([0, 1, 2], size=len(data))  # 0: BP, 1: Diabetes, 2: Obesity

# Features and labels
X = data[['nutriscore_score', 'fat_100g', 'energy-kcal_100g']]
y = data['condition']

# Train Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# Function to evaluate products for a given condition
def evaluate_condition(condition):
    filtered_products = []
    for idx, row in data.iterrows():
        product = row.to_dict()
        predicted_condition = rf_model.predict([[product['nutriscore_score'], product['fat_100g'], product['energy-kcal_100g']]])[0]
        if predicted_condition == condition:
            filtered_products.append(product)
    
    return filtered_products

# Function to recommend food and quantity
def recommend_food(condition_input):
    condition_map = {'bp': 0, 'diabetes': 1, 'obesity': 2}
    
    condition = condition_map.get(condition_input.lower())
    if condition is None:
        return "Invalid condition. Please enter 'bp', 'diabetes', or 'obesity'."
    
    products_for_condition = evaluate_condition(condition)
    
    if len(products_for_condition) == 0:
        return f"No products found for condition: {condition_input}"
    
    recommended_foods = []
    for product in products_for_condition:
        recommended_foods.append({
            "product_name": product['product_name'],
            "image_url": product['image_url'],
            "recommended_quantity": "Moderate (100-200g)",  # Customize based on actual data
            "reason": f"Good for {condition_input} health",
            "quantity": product['quantity'],
            "categories": product['categories'],
            "labels": product['labels']
        })
    
    return recommended_foods

# Flask route for the homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input_condition = request.form['condition']
        recommended_foods = recommend_food(user_input_condition)
        
        if isinstance(recommended_foods, str):  # If there's an error message
            return render_template('index.html', message=recommended_foods)
        return render_template('index.html', foods=recommended_foods)
    
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
