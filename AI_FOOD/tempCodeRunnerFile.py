<<<<<<< HEAD
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load dataset (replace with the correct path to your dataset)
dataset = pd.read_csv('foodpr_cleaned_dataset (3).csv')  # Update path if needed

# Function to get product details from dataset using barcode
def get_product_details(barcode):
    barcode = str(barcode).strip()
    dataset['code'] = dataset['code'].astype(str).str.strip()  # Ensures no extra spaces
    product = dataset[dataset['code'] == barcode]
    
    if not product.empty:
        details = {
            'product_name': product['product_name'].values[0],
            'brands': product['brands'].values[0],
            'categories': product['categories'].values[0],
            'ingredients': product['ingredients_text'].values[0],
            'nutriscore': product['nutriscore_score'].values[0],
            'nova_group': product['nova_group'].values[0],
            'energy': product['energy-kcal_100g'].values[0],
            'image_url': product['image_url'].values[0]
        }
        return details
    else:
        return {'error': 'Product not found in dataset'}

# Route to display the scan page
@app.route('/')
def home():
    return render_template('scan.html')

# Route to handle barcode code input and display product details
@app.route('/scan', methods=['POST'])
def scan_barcode():
    barcode_code = request.form['barcode_code']
    product_details = get_product_details(barcode_code)

    if 'error' in product_details:
        return render_template('scan.html', error=product_details['error'])
    
    return render_template('scan.html', product=product_details)

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load dataset (replace with the correct path to your dataset)
dataset = pd.read_csv('foodpr_cleaned_dataset (3).csv')  # Update path if needed

# Function to get product details from dataset using barcode
def get_product_details(barcode):
    barcode = str(barcode).strip()
    dataset['code'] = dataset['code'].astype(str).str.strip()  # Ensures no extra spaces
    product = dataset[dataset['code'] == barcode]
    
    if not product.empty:
        details = {
            'product_name': product['product_name'].values[0],
            'brands': product['brands'].values[0],
            'categories': product['categories'].values[0],
            'ingredients': product['ingredients_text'].values[0],
            'nutriscore': product['nutriscore_score'].values[0],
            'nova_group': product['nova_group'].values[0],
            'energy': product['energy-kcal_100g'].values[0],
            'image_url': product['image_url'].values[0]
        }
        return details
    else:
        return {'error': 'Product not found in dataset'}

# Route to display the scan page
@app.route('/')
def home():
    return render_template('scan.html')

# Route to handle barcode code input and display product details
@app.route('/scan', methods=['POST'])
def scan_barcode():
    barcode_code = request.form['barcode_code']
    product_details = get_product_details(barcode_code)

    if 'error' in product_details:
        return render_template('scan.html', error=product_details['error'])
    
    return render_template('scan.html', product=product_details)

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 787bc04 (Added new files and updates)
