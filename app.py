import os
import werkzeug
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from email_parser import parse_eml_bytes, EmailParseError
from classifier import ModelPredictor

app = Flask(__name__)

# Security & Upload Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Machine Learning Models ONCE at application startup
predictor = None
try:
    predictor = ModelPredictor(models_dir=os.path.join(os.path.dirname(__file__), 'models'))
except Exception as e:
    print(f"CRITICAL ERROR loading models: {e}")

@app.route('/')
def index():
    """Render main application dashboard."""
    return render_template('index.html')

@app.route('/api/classify', methods=['POST'])
def classify_emails():
    """
    Classification Endpoint.
    Accepts multipart/form-data with:
    - 'files': one or multiple .eml files
    - 'models': model identifiers ('naive_bayes', 'knn', 'decision_tree', 'all')
    """
    if not predictor or not predictor.is_loaded:
        return jsonify({
            "success": False,
            "error": "Lỗi máy chủ: Các mô hình học máy chưa được tải lên bộ nhớ."
        }), 500

    # Retrieve files from request
    uploaded_files = request.files.getlist('files')
    if not uploaded_files or len(uploaded_files) == 0:
        return jsonify({
            "success": False,
            "error": "Chưa có file email nào được gửi lên."
        }), 400

    # Retrieve requested models
    models_param = request.form.getlist('models')
    if not models_param:
        raw_m = request.form.get('models', '')
        models_param = [m.strip() for m in raw_m.split(',') if m.strip()]

    if not models_param:
        models_param = ['naive_bayes', 'knn', 'decision_tree']
    elif 'all' in models_param or 'all_models' in models_param:
        models_param = ['naive_bayes', 'knn', 'decision_tree']

    results = []

    for file_obj in uploaded_files:
        filename = secure_filename(file_obj.filename or "email.eml")
        
        # Check file extension
        if not filename.lower().endswith('.eml'):
            results.append({
                "filename": filename,
                "error": "Định dạng file không hợp lệ. Chỉ hỗ trợ file .eml."
            })
            continue

        try:
            raw_bytes = file_obj.read()
            if not raw_bytes:
                results.append({
                    "filename": filename,
                    "error": "File rỗng."
                })
                continue

            # Step 1-4: Parse EML structure
            parsed_data = parse_eml_bytes(raw_bytes, filename=filename)
            subject = parsed_data['subject']
            combined_text = parsed_data['combined_text']

            if not combined_text.strip():
                results.append({
                    "filename": filename,
                    "subject": subject,
                    "error": "Email không chứa tiêu đề hoặc nội dung có thể trích xuất."
                })
                continue

            # Step 5-8: Preprocessing, vectorizer transform & predictions
            prediction_res = predictor.predict(combined_text, selected_models=models_param)

            results.append({
                "filename": filename,
                "subject": subject,
                "predictions": prediction_res['predictions'],
                "processed_text": prediction_res['processed_text']
            })

        except EmailParseError as e:
            results.append({
                "filename": filename,
                "error": f"Lỗi đọc Email: {str(e)}"
            })
        except Exception as e:
            results.append({
                "filename": filename,
                "error": f"Lỗi phân loại Email: {str(e)}"
            })

    return jsonify({
        "success": True,
        "results": results
    })

if __name__ == '__main__':
    print("Starting Spam Email Classifier Web Application on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=False)
