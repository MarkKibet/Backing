from flask import Flask
from flask_migrate import Migrate
from Models import db
from Advocates import advocates_bp
from Cases import cases_bp
from Register import register_bp  # Import register blueprint
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)
    CORS(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(advocates_bp, url_prefix='/api/advocates')
    app.register_blueprint(cases_bp, url_prefix='/api/cases')
    app.register_blueprint(register_bp, url_prefix='/api/register')  

    # Root route
    @app.route('/')
    def home():
        return "<h1>Welcome to the Advocates and Cases API</h1>"

    # Favicon route
    @app.route('/favicon.ico')
    def favicon():
        return "", 204  # Respond with no content for favicon requests

    return app

# Run the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
