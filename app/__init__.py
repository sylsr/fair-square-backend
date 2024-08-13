from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # APISpec configuration for automatic doc generation
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Email API',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0.0'
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',  # URI for exposing Swagger
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI for Swagger UI
    })
    docs = FlaskApiSpec(app)

    from app.routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register your routes with the docs
    with app.app_context():  # Ensure this is done within app context
        docs.register_existing_resources()

    return app

