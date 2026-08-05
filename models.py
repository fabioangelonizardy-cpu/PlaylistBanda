from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    senha_hash = db.Column(
        db.String(300),
        nullable=False
    )

    votos = db.relationship(
        "Voto",
        backref="usuario",
        cascade="all, delete-orphan"
    )

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


@login_manager.user_loader
def carregar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))


class Musica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    artista = db.Column(db.String(100), nullable=False)
    sugerida_por = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(300))
    observacao = db.Column(db.Text)

    votos = db.relationship(
        "Voto",
        backref="musica",
        cascade="all, delete-orphan"
    )

    @property
    def votos_sim(self):
        return sum(
            1 for voto in self.votos
            if voto.escolha is True
        )

    @property
    def votos_nao(self):
        return sum(
            1 for voto in self.votos
            if voto.escolha is False
        )

    @property
    def status(self):
        if self.votos_sim >= 4:
            return "Aprovada"

        if self.votos_nao >= 4:
            return "Rejeitada"

        return "Em votação"

    def __repr__(self):
        return f"<Musica {self.titulo}>"


class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    escolha = db.Column(
        db.Boolean,
        nullable=False
    )

    musica_id = db.Column(
        db.Integer,
        db.ForeignKey("musica.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            "musica_id",
            name="voto_unico_por_usuario"
        ),
    )