from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)
data = pd.read_csv('final_dataset.csv')
pipe = pickle.load(open("RidgeModel.pkl", 'rb'))

@app.route('/')
def index():
    bedrooms = sorted(data['beds'].unique())
    bathrooms = sorted(data['baths'].unique())
    sizes = sorted(data['size'].unique())
    zip_codes = sorted(data['zip_code'].unique())

    return render_template('index.html', bedrooms=bedrooms, bathrooms=bathrooms, sizes=sizes, zip_codes=zip_codes)

@app.route('/predict', methods=['POST'])
def predict():
    bedrooms = request.form.get('beds')
    bathrooms = request.form.get('baths')
    size = request.form.get('size')
    zipcode = request.form.get('zip_code')

    # Create a DataFrame with the input data
    input_data = pd.DataFrame([[bedrooms, bathrooms, size, zipcode]],
                               columns=['beds', 'baths', 'size', 'zip_code'])

    print("Input Data:")
    print(input_data)

    # Convert 'baths' column to numeric with errors='coerce'
    input_data['baths'] = pd.to_numeric(input_data['baths'], errors='coerce')

    # Convert input data to numeric types
    input_data['beds'] = pd.to_numeric(input_data['beds'], errors='coerce')
    input_data['size'] = pd.to_numeric(input_data['size'], errors='coerce')
    input_data['zip_code'] = pd.to_numeric(input_data['zip_code'], errors='coerce')

    # Handle NaN values or missing values
    input_data.fillna({
        'beds': data['beds'].mode()[0],  # Replace NaN with mode of 'beds' column
        'baths': data['baths'].mode()[0],  # Replace NaN with mode of 'baths' column
        'size': data['size'].median(),  # Replace NaN with median of 'size' column
        'zip_code': data['zip_code'].mode()[0]  # Replace NaN with mode of 'zip_code' column
    }, inplace=True)

    print("Processed Input Data:")
    print(input_data)

    # Predict the price
    prediction = pipe.predict(input_data)[0]

    return str(prediction)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
