from flask import Flask, request, jsonify
import joblib
import pickle
import logging
import numpy as np
from flask_cors import CORS  # Allow cross-origin requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__)
CORS()

# Paths to model and encoders
MODEL_PATH = "Models/random_forest_model.pkl"
ENCODERS_PATH = "Models/label_encoders.pkl"

# Load model and encoders
logging.info("Loading model and encoders...")
model = joblib.load(MODEL_PATH)
with open(ENCODERS_PATH, 'rb') as f:
    label_encoders = pickle.load(f)

def preprocess_input(data):
    """Preprocess input data by removing quotes and ensuring correct types."""
    preprocessed_data = {}
    for key in data:
        value = data[key]
        # Remove single quotes if present and convert to appropriate type
        if isinstance(value, str):
            value = value.strip("'")  # Remove single quotes
        preprocessed_data[key] = value
    return preprocessed_data

def predict_top_n_cases(input_data, n=3):
    # Encode the input data
    try:
        input_data_encoded = [
            label_encoders['SamplingPointID'].transform([input_data['SamplingPointID']])[0],
            label_encoders['TestID'].transform([input_data['TestID']])[0],
            label_encoders['ExpertiseLevelID'].transform([input_data['ExpertiseLevelID']])[0]
        ]
    except KeyError as e:
        raise ValueError(f"Unseen label: {str(e)}")
    
    probabilities = model.predict_proba([input_data_encoded])[0]
    top_n_indices = np.argsort(probabilities)[-n:][::-1]
    top_n_predictions = label_encoders['AnalystID'].inverse_transform(top_n_indices)
    top_n_probabilities = probabilities[top_n_indices]

    return list(zip(top_n_predictions, top_n_probabilities))

@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415
    
    data = request.get_json()
    logging.info(f"Received data for prediction: {data}")

    # Validate required keys
    required_keys = ["SamplingPointID", "TestID", "ExpertiseLevelID"]
    for key in required_keys:
        if key not in data:
            return jsonify({"error": f"Missing required key: {key}"}), 400

    try:
        # Preprocess the input data
        input_data = preprocess_input(data)
        top_n_predictions = predict_top_n_cases(input_data, n=3)
        
        response = {}
        for i, (pred, prob) in enumerate(top_n_predictions, start=1):
            response[f'Prediction {i}'] = int(pred)
            response[f'Confidence {i}'] = float(prob)
        
        return jsonify(response)
    except ValueError as e:
        logging.error(str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
