document.addEventListener("DOMContentLoaded", function () {
    const campoPesquisa = document.getElementById("pesquisa-musica");
    const botoesFiltro = document.querySelectorAll(".filtro");
    const musicas = document.querySelectorAll(".musica");
    const mensagemNenhumResultado =
        document.getElementById("nenhum-resultado");

    let filtroAtual = "todas";

    function normalizarTexto(texto) {
        return texto
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function filtrarMusicas() {
        const pesquisa = normalizarTexto(campoPesquisa.value);
        let quantidadeVisivel = 0;

        musicas.forEach(function (musica) {
            const textoMusica = normalizarTexto(
                musica.dataset.pesquisa || ""
            );

            const statusMusica = musica.dataset.status;

            const correspondePesquisa =
                textoMusica.includes(pesquisa);

            const correspondeStatus =
                filtroAtual === "todas" ||
                statusMusica === filtroAtual;

            if (correspondePesquisa && correspondeStatus) {
                musica.style.display = "block";
                quantidadeVisivel++;
            } else {
                musica.style.display = "none";
            }
        });

        if (mensagemNenhumResultado) {
            mensagemNenhumResultado.style.display =
                musicas.length > 0 && quantidadeVisivel === 0
                    ? "block"
                    : "none";
        }
    }

    campoPesquisa.addEventListener("input", filtrarMusicas);

    botoesFiltro.forEach(function (botao) {
        botao.addEventListener("click", function () {
            botoesFiltro.forEach(function (outroBotao) {
                outroBotao.classList.remove("ativo");
            });

            botao.classList.add("ativo");
            filtroAtual = botao.dataset.status;

            filtrarMusicas();
        });
    });
});