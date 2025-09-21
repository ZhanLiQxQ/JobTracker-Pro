from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from matcher import find_best_matches
import fitz  # PyMuPDF
import docx # python-docx
import io
import os

app = Flask(__name__)
CORS(app)

# --- Configuration section ---
# Read configuration from environment variables, use defaults if not provided
JAVA_BACKEND_INTERNAL_JOBS_URL = os.environ.get("JAVA_BACKEND_INTERNAL_JOBS_URL", "http://localhost:8080/api/internal/jobs")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "thisisaramdomandVeryLongStringtoMakeItASecretKey155423asc5assajci,w,YAJCB")

def extract_text(file_stream, filename):
    """Extract text from file stream based on file extension"""
    text = ""
    if filename.lower().endswith('.pdf'):
        # Parse PDF
        pdf_document = fitz.open(stream=file_stream.read(), filetype="pdf")
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
    elif filename.lower().endswith('.docx'):
        # Parse DOCX
        doc = docx.Document(io.BytesIO(file_stream.read()))
        for para in doc.paragraphs:
            text += para.text + '\n'
    else:
        raise ValueError("Unsupported file type")
    return text

@app.route('/recommend_file', methods=['POST'])
def recommend_from_file():
    # 1. Check if file exists
    if 'resume_file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['resume_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        print(f"Processing file: {file.filename}")
        
        # 2. Extract plain text from uploaded file
        if file.stream is None:
            return jsonify({"error": "File stream is None"}), 400
            
        resume_text = extract_text(file.stream, file.filename)
        print(f"Extracted text length: {len(resume_text) if resume_text else 0}")
        
        if not resume_text or len(resume_text.strip()) == 0:
            return jsonify({"error": "No text extracted from file"}), 400

        # 3. Use internal API key to request internal interface to get all jobs
        headers = {'X-Internal-API-Key': INTERNAL_API_KEY}
        print(f"Requesting jobs from: {JAVA_BACKEND_INTERNAL_JOBS_URL}")
        response = requests.get(JAVA_BACKEND_INTERNAL_JOBS_URL, headers=headers)
        response.raise_for_status()
        all_jobs = response.json()
        print(f"Retrieved {len(all_jobs) if all_jobs else 0} jobs from backend")
        
        if not all_jobs:
            return jsonify({"error": "No jobs found in backend"}), 500

        # 4. Call matching function to get recommendation results
        recommended_jobs = find_best_matches(resume_text, all_jobs)
        print(f"Generated {len(recommended_jobs) if recommended_jobs else 0} recommendations")

        # 5. Return sorted job list
        return jsonify(recommended_jobs)

    except ValueError as e:
        print(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        return jsonify({"error": f"Failed to fetch jobs from Java backend: {e}"}), 500
    except Exception as e:
        # Catch all other potential errors
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)