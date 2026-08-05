from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db
from models import Musica, Voto, Usuario


main = Blueprint("main", __name__)


@main.route("/")
@login_required
def home():
    todas = db.session.execute(
        db.select(Musica).order_by(
            Musica.id.desc()
        )
    ).scalars().all()

    musicas = [
        musica
        for musica in todas
        if musica.status == "Em votação"
    ]

    return render_template(
        "index.html",
        musicas=musicas
    )

@main.route("/playlist")
@login_required
def playlist():

    musicas = db.session.execute(
        db.select(Musica).order_by(
            Musica.artista,
            Musica.titulo
        )
    ).scalars().all()

    musicas = [
        musica
        for musica in musicas
        if musica.status == "Aprovada"
    ]

    return render_template(
        "playlist.html",
        musicas=musicas
    )

@main.route("/rejeitadas")
@login_required
def rejeitadas():

    musicas = db.session.execute(
        db.select(Musica).order_by(
            Musica.artista,
            Musica.titulo
        )
    ).scalars().all()

    musicas = [
        musica
        for musica in musicas
        if musica.status == "Rejeitada"
    ]

    return render_template(
        "rejeitadas.html",
        musicas=musicas
    )

@main.route("/adicionar", methods=["GET", "POST"])
@login_required
def adicionar():
    if request.method == "POST":
        titulo = request.form.get(
            "titulo",
            ""
        ).strip()

        artista = request.form.get(
            "artista",
            ""
        ).strip()

        link = request.form.get(
            "link",
            ""
        ).strip()

        observacao = request.form.get(
            "observacao",
            ""
        ).strip()

        if not titulo or not artista:
            flash(
                "Preencha os campos obrigatórios.",
                "erro"
            )

            return render_template(
                "adicionar.html"
            )

        nova_musica = Musica(
            titulo=titulo,
            artista=artista,
            sugerida_por=current_user.nome,
            link=link,
            observacao=observacao
        )

        db.session.add(nova_musica)
        db.session.commit()

        flash(
            "Música adicionada com sucesso!",
            "sucesso"
        )

        return redirect(
            url_for("main.home")
        )

    return render_template(
        "adicionar.html"
    )


@main.route("/votar/<int:musica_id>", methods=["POST"])
@login_required
def votar(musica_id):
    musica = db.get_or_404(
        Musica,
        musica_id
    )

    escolha_recebida = request.form.get(
        "escolha",
        ""
    )

    if escolha_recebida not in ["sim", "nao"]:
        return "Voto inválido.", 400

    escolha = escolha_recebida == "sim"

    voto_existente = db.session.execute(
        db.select(Voto).where(
            Voto.musica_id == musica.id,
            Voto.usuario_id == current_user.id
        )
    ).scalar_one_or_none()

    if voto_existente:
        voto_existente.escolha = escolha
    else:
        novo_voto = Voto(
            escolha=escolha,
            musica_id=musica.id,
            usuario_id=current_user.id
        )

        db.session.add(novo_voto)

    db.session.commit()

    flash(
        "Seu voto foi registrado.",
        "sucesso"
    )

    if request.referrer:
        return redirect(request.referrer)

    return redirect(
        url_for("main.home")
    )


@main.route("/musica/<int:musica_id>")
@login_required
def detalhes_musica(musica_id):
    musica = db.get_or_404(
        Musica,
        musica_id
    )

    usuarios = db.session.execute(
        db.select(Usuario).order_by(
            Usuario.nome
        )
    ).scalars().all()

    votos_sim = []
    votos_nao = []
    nao_votaram = []

    votos_por_usuario = {
        voto.usuario_id: voto.escolha
        for voto in musica.votos
    }

    for usuario in usuarios:
        if usuario.id not in votos_por_usuario:
            nao_votaram.append(usuario)

        elif votos_por_usuario[usuario.id] is True:
            votos_sim.append(usuario)

        else:
            votos_nao.append(usuario)

    return render_template(
        "detalhes_musica.html",
        musica=musica,
        votos_sim=votos_sim,
        votos_nao=votos_nao,
        nao_votaram=nao_votaram
    )

@main.route("/musica/<int:musica_id>/editar", methods=["GET", "POST"])
@login_required
def editar_musica(musica_id):
    musica = db.get_or_404(Musica, musica_id)

    if musica.sugerida_por != current_user.nome:
        flash(
            "Você só pode editar músicas sugeridas por você.",
            "erro"
        )

        return redirect(
            url_for(
                "main.detalhes_musica",
                musica_id=musica.id
            )
        )

    if request.method == "POST":
        titulo = request.form.get(
            "titulo",
            ""
        ).strip()

        artista = request.form.get(
            "artista",
            ""
        ).strip()

        link = request.form.get(
            "link",
            ""
        ).strip()

        observacao = request.form.get(
            "observacao",
            ""
        ).strip()

        if not titulo or not artista:
            flash(
                "Preencha os campos obrigatórios.",
                "erro"
            )

            return render_template(
                "editar_musica.html",
                musica=musica
            )

        musica.titulo = titulo
        musica.artista = artista
        musica.link = link
        musica.observacao = observacao

        db.session.commit()

        flash(
            "Música atualizada com sucesso!",
            "sucesso"
        )

        return redirect(
            url_for(
                "main.detalhes_musica",
                musica_id=musica.id
            )
        )

    return render_template(
        "editar_musica.html",
        musica=musica
    )

@main.route("/musica/<int:musica_id>/remover", methods=["POST"])
@login_required
def remover_musica(musica_id):
    musica = db.get_or_404(Musica, musica_id)

    if musica.sugerida_por != current_user.nome:
        flash(
            "Você só pode remover músicas sugeridas por você.",
            "erro"
        )

        return redirect(
            url_for(
                "main.detalhes_musica",
                musica_id=musica.id
            )
        )

    titulo = musica.titulo

    db.session.delete(musica)
    db.session.commit()

    flash(
        f'A música "{titulo}" foi removida.',
        "sucesso"
    )

    return redirect(url_for("main.home"))