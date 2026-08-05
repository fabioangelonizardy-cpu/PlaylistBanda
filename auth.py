from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from extensions import db
from models import Usuario


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")

        usuario = db.session.execute(
            db.select(Usuario).where(
                Usuario.nome == nome
            )
        ).scalar_one_or_none()

        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)

            flash(
                "Login realizado com sucesso!",
                "sucesso"
            )

            return redirect(url_for("main.home"))

        flash(
            "Nome ou senha incorretos.",
            "erro"
        )

    usuarios = db.session.execute(
        db.select(Usuario).order_by(Usuario.nome)
    ).scalars().all()

    return render_template(
        "login.html",
        usuarios=usuarios
    )


@auth.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "Você saiu da sua conta.",
        "sucesso"
    )

    return redirect(url_for("auth.login"))