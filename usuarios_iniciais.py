from extensions import db
from models import Usuario


def criar_usuarios_iniciais():
    usuarios_iniciais = [
        ("Fábio", "123"),
        ("Sofia", "1234"),
        ("Diogo", "12345"),
        ("Yugo", "123456"),
        ("Vicente", "1234567"),
        ("Gabriel", "12345678")
    ]

    for nome, senha in usuarios_iniciais:
        usuario_existente = db.session.execute(
            db.select(Usuario).where(
                Usuario.nome == nome
            )
        ).scalar_one_or_none()

        if not usuario_existente:
            novo_usuario = Usuario(nome=nome)
            novo_usuario.definir_senha(senha)

            db.session.add(novo_usuario)

    db.session.commit()