from flask import Flask
from controllers import controllers as controllers_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(controllers_bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)