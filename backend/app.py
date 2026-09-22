import os
from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.database.db import db
from backend.database.models import NLPModel
from backend.routes import auth_bp, analysis_bp, history_bp, report_bp
from backend.utils.helpers import api_response

def create_app(config_class=Config):
    """Flask Application Factory."""
    app = Flask(
        __name__,
        static_folder='../frontend/static',
        template_folder='../frontend/templates'
    )
    app.config.from_object(config_class)

    # Enable CORS for REST API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize SQLAlchemy database instance
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(report_bp)

    # Create tables & seed default NLP model metadata inside app context
    with app.app_context():
        db.create_all()
        _seed_initial_metadata()

    # Register Error Handlers
    @app.errorhandler(404)
    def handle_not_found(error):
        return api_response(success=False, message="The requested resource was not found.", status_code=404)

    @app.errorhandler(500)
    def handle_server_error(error):
        return api_response(
            success=False, 
            message="An internal server error occurred. Please try again later.", 
            status_code=500
        )

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """System health & readiness check endpoint."""
        return api_response(
            success=True, 
            message="System operational.", 
            data={
                'status': 'healthy', 
                'version': '1.0.0', 
                'project': 'AI-Powered Bias & Fairness Detection System'
            }, 
            status_code=200
        )

    return app


def _seed_initial_metadata():
    """Seed initial NLP model metadata without claiming fake training accuracy."""
    try:
        if not NLPModel.query.filter_by(modelName='valhalla/distilbart-mnli-12-3').first():
            default_model = NLPModel(
                modelName='valhalla/distilbart-mnli-12-3',
                modelVersion='1.0.0-zero-shot-hybrid',
                accuracy=None,  # Not hardcoded / fake
                languageSupported='en',
                description='Hybrid Zero-Shot Multi-label Transformer combined with rule-based pattern matching for 7 bias categories.'
            )
            db.session.add(default_model)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[App Init Warning]: Model metadata seed failed: {str(e)}")


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
