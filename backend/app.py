import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from models import init_db

# 로컬 개발 시 .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

app = Flask(__name__, static_folder=DIST_DIR, static_url_path='')
CORS(app)

from routes.respondent import respondent_bp
from routes.diagnosis import diagnosis_bp
from routes.roadmap import roadmap_bp

app.register_blueprint(respondent_bp, url_prefix='/api')
app.register_blueprint(diagnosis_bp, url_prefix='/api')
app.register_blueprint(roadmap_bp, url_prefix='/api')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    file_path = os.path.join(DIST_DIR, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')


with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
