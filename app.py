import os

from flask import Flask

from extensions import db, login_manager
from auth import auth
from routes import main
from usuarios_iniciais import criar_usuarios_iniciais


def criar_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "troque-esta-chave"
    )

    pasta_projeto = os.path.dirname(
        os.path.abspath(__file__)
    )

    caminho_banco = os.path.join(
        pasta_projeto,
        "instance",
        "bandplaylist.db"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{caminho_banco}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Faça login para acessar esta página."
    )
    login_manager.login_message_category = "erro"

    app.register_blueprint(auth)
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        criar_usuarios_iniciais()

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=True)