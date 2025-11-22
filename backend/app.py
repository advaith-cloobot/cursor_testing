from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf', 'png'}
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database.db')

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import and register blueprints
from routes.repos import repos_bp
from routes.accounts import accounts_bp
from routes.sources import sources_bp

app.register_blueprint(repos_bp, url_prefix='/api')
app.register_blueprint(accounts_bp, url_prefix='/api')
app.register_blueprint(sources_bp, url_prefix='/api')

# Initialize database
from models import init_db
init_db(app.config['DATABASE'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)

