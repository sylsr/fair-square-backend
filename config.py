import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "app.db")}'  # Creates app.db in your project directory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTMARK_API_TOKEN = os.getenv('POSTMARK_API_TOKEN')

    @staticmethod
    def init_app(app):
        pass
