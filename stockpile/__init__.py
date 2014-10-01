from flask import Flask
from stockpile.models import db


def create_app(object_name='stockpile.settings.DevConfig', env="dev"):
    app = Flask(__name__)

    app.config.from_object(object_name)
    app.config['ENV'] = env

    #init SQLAlchemy
    db.init_app(app)

    # register our blueprints
    from interface.main import mod as interfaceMod
    app.register_blueprint(interfaceMod)

    return app

app = create_app()

if __name__ == '__main__':
    app.run()