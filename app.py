# app.py

import pandas as pd
import numpy as np
import joblib
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# Load the pre-trained pipeline
pipeline = joblib.load("credit_card_pipeline.pkl")

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_fraud', methods=['POST'])
def find_fraud():
    if 'file' not in request.files:
        flash('No file part in the request.')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No file selected for uploading.')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            if filename.endswith('.csv'):
                data = pd.read_csv(filepath)
            elif filename.endswith('.xlsx'):
                data = pd.read_excel(filepath)
            else:
                flash('Unsupported file format.')
                return redirect(url_for('index'))
        except Exception as e:
            flash('Error reading the file. Please ensure it is a valid CSV or Excel file.')
            return redirect(url_for('index'))
        
        # Check for required columns
        required_columns = {'Class'}
        if not required_columns.issubset(data.columns):
            flash("Uploaded file must contain the 'Class' column.")
            return redirect(url_for('index'))
        
        # Drop duplicates and unnecessary columns if 'Time' exists
        if 'Time' in data.columns:
            data = data.drop(['Time'], axis=1)
        
        data = data.drop_duplicates()
        
        X = data.drop(['Class'], axis=1)
        
        # Predict using the pipeline
        predictions = pipeline.predict(X)
        
        # Add predictions to the dataframe
        data['Prediction'] = predictions
        
        # Filter for fraudulent transactions
        frauds = data[data['Prediction'] == 1]
        
        # Save the result to a new Excel file
        fraud_file = os.path.join(app.config['UPLOAD_FOLDER'], 'fraud_transactions.xlsx')
        frauds.to_excel(fraud_file, index=False)
        
        return send_file(fraud_file, as_attachment=True, download_name='fraud_transactions.xlsx')
    else:
        flash('Allowed file types are CSV and Excel.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
