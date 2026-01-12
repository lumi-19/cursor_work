"""
THE_WORLD - WebGIS Disaster and AQI Monitoring System
Main Flask Application Entry Point
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
from app.config import config
from app.database import db, init_db


def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    init_db(app)
    
    # Register blueprints
    from app.routes import disasters, aqi, cities, comparison, correlation, download, chatbot
    
    app.register_blueprint(disasters.bp, url_prefix='/api/disasters')
    app.register_blueprint(aqi.bp, url_prefix='/api/aqi')
    app.register_blueprint(cities.bp, url_prefix='/api/cities')
    app.register_blueprint(comparison.bp, url_prefix='/api/comparison')
    app.register_blueprint(correlation.bp, url_prefix='/api/correlation')
    app.register_blueprint(download.bp, url_prefix='/api/download')
    app.register_blueprint(chatbot.bp, url_prefix='/api/chatbot')
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'THE_WORLD API - WebGIS Disaster and AQI Monitoring System',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'disasters': '/api/disasters',
                'aqi': '/api/aqi',
                'cities': '/api/cities',
                'comparison': '/api/comparison',
                'correlation': '/api/correlation',
                'download': '/api/download',
                'chatbot': '/api/chatbot'
            }
        })
    
    # Health check route
    @app.route('/api/health')
    def health():
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'service': 'THE_WORLD API',
            'database': db_status,
            'version': '1.0.0'
        })
    
        # Error handlers
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found'}), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = app.config['FLASK_RUN_PORT']
    host = app.config['FLASK_RUN_HOST']
    debug = app.config.get('DEBUG', True)
    app.run(host=host, port=port, debug=debug)
