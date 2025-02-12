import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from flask import Flask, render_template, request

# Initialize Flask app
app = Flask(__name__)

# Load product dataset
file_path = r"foodpr_cleaned_dataset (3).csv"
df = pd.read_csv(file_path)

# Load USDA dataset
usda_file_path = r"USDA.csv"
usda_df = pd.read_csv(usda_file_path)

# Rename USDA columns for consistency
usda_df.rename(columns={
    "Description": "product_name",
    "Calories": "energy-kcal_100g",
    "TotalFat": "fat_100g",
    "Sodium": "sodium_100g",
    "Sugar": "sugar_100g",
    "Protein": "protein_100g"
}, inplace=True)

# Keep only necessary columns from USDA dataset
usda_df = usda_df[['product_name', 'energy-kcal_100g', 'fat_100g', 'sodium_100g', 'sugar_100g', 'protein_100g']]

# Drop rows with missing critical values in USDA dataset
usda_df.dropna(subset=["sodium_100g", "sugar_100g", "protein_100g"], inplace=True)

# Define expected columns for consistency
expected_columns = ["energy-kcal_100g", "fat_100g", "sodium_100g", "sugar_100g", "protein_100g"]

# Fill missing values in USDA dataset with mean values
for col in expected_columns:
    usda_df[col].fillna(usda_df[col].mean(), inplace=True)

# Health condition mapping function
def map_condition(row):
    if row['sugar_100g'] > 10 or row['energy-kcal_100g'] > 400:
        return 'type 2 diabetes'
    elif row['sodium_100g'] > 1.5:
        return 'hypertension'
    elif row['fat_100g'] > 15:
        return 'high cholesterol'
    elif row['energy-kcal_100g'] < 150:
        return 'underweight'
    else:
        return 'normal'

# Apply condition mapping on USDA dataset
usda_df['condition'] = usda_df.apply(map_condition, axis=1)

# Encode condition labels
label_encoder = LabelEncoder()
usda_df['condition_label'] = label_encoder.fit_transform(usda_df['condition'])

# Normalize numerical features for model training
scaler = StandardScaler()
usda_df[expected_columns] = scaler.fit_transform(usda_df[expected_columns])

# Train Random Forest model on USDA dataset
X = usda_df[expected_columns]
y = usda_df['condition_label']
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# Recommendation function
def recommend_food(condition_input):
    print(f"User selected Condition: {condition_input}")

    # Validate condition
    if condition_input not in usda_df['condition'].values:
        print("Condition not found in USDA dataset!")
        return f"No data found for condition: {condition_input}"

    # Get condition label
    condition_code = usda_df.loc[usda_df['condition'] == condition_input, 'condition_label'].values[0]

    # Filter and recommend products from df (product dataset)
    recommended_products = []
    for _, product in df.iterrows():
        # Extract relevant nutrition info
        nutrition_features = np.array([
            product.get('energy-kcal_100g', np.nan),
            product.get('fat_100g', np.nan),
            product.get('sodium_100g', np.nan),
            product.get('sugar_100g', np.nan),
            product.get('protein_100g', np.nan)
        ]).reshape(1, -1)

        # Predict condition for the product
        predicted_label = rf_model.predict(nutrition_features)[0]

        # Match with user’s condition
        if predicted_label == condition_code:
            recommended_products.append({
                "product_name": product.get('product_name', 'Unknown'),
                "image_url": product.get('image_url', ''),
                "recommended_quantity": "Based on your condition",
                "reason": f"Good for {condition_input} health",
                "quantity": product.get('quantity', 'Unknown'),
                "labels": product.get('labels', 'Unknown')
            })

    return recommended_products if recommended_products else f"No products found for condition: {condition_input}"

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input_condition = request.form['condition']

        recommended_foods = recommend_food(user_input_condition)

        if isinstance(recommended_foods, str):  
            return render_template('index.html', message=recommended_foods)

        return render_template('index.html', foods=recommended_foods)

    return render_template('index.html')

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
