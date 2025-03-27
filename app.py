from flask import Flask
from flask_jwt_extended import JWTManager
from config import config
from extensions import mysql
from flask_cors import CORS
from flask_mail import Mail

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(config['development'])

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # For Gmail; change this if you're using a different provider
app.config['MAIL_PORT'] = 587  # SMTP port for TLS
app.config['MAIL_USE_TLS'] = True  # Use TLS for secure connection
app.config['MAIL_USE_SSL'] = False  # Don't use SSL
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Your email address (sender's address)
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Your email password (use app password for Gmail)
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'  # Default sender email

# Initialize the Mail object
mail = Mail(app)

# Initialize Extensions
mysql.init_app(app)
jwt = JWTManager(app)
CORS(app)  # Allow cross-origin requests

# Homepage Route
@app.route('/')
def home():
    return 'Welcome to StyleCraft API!'

# Import Blueprints
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
