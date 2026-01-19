"""
RaceVision Flask Application
Main Flask application with modular route structure
"""

from flask import Flask, send_from_directory
import logging
import os

# Import route blueprints
from routes.drivers import drivers_bp
from routes.constructors import constructors_bp
from routes.seasons import seasons_bp
from routes.api import api_bp
from routes.eda import eda_bp
from routes.ml import ml_bp
from routes.home_eda import home_eda_bp

# Import configuration
from config.mongo import mongo_db

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    app.register_blueprint(home_eda_bp)  # New EDA home (register first to override /)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(constructors_bp)
    app.register_blueprint(seasons_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(eda_bp)
    app.register_blueprint(ml_bp)
    
    # Error handling
    @app.errorhandler(404)
    def not_found(error):
        return 'Page not found', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return 'Internal server error', 500
    
    # Test route for chart debugging
    @app.route('/test-chart')
    def test_chart():
        return send_from_directory('.', 'test_chart.html')
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.')
    debug = app.config.get('DEBUG', False)
    
    print(f"Starting RaceVision Flask application on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Dashboard: http://{host}:{port}/")
    print(f"API Documentation: http://{host}:{port}/api/drivers")
    
    app.run(host=host, port=port, debug=debug)
