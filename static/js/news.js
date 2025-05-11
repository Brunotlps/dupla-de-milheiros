document.addEventListener("DOMContentLoaded", function () {
    function carregarNoticias() {
        fetch("/news/")
            .then(response => response.text())
            .then(html => {
                let parser = new DOMParser();
                let doc = parser.parseFromString(html, "text/html");
                let novasNoticias = doc.querySelector("#noticias-container").innerHTML;
                
                // Só atualiza se houver mudanças
                let containerAtual = document.querySelector("#noticias-container");
                if (containerAtual.innerHTML.trim() !== novasNoticias.trim()) {
                    containerAtual.innerHTML = novasNoticias;
                }
            })
            .catch(error => console.error("Erro ao carregar notícias:", error));
    }
    

    // Atualiza as notícias ao clicar no botão
    document.getElementById("atualizarNoticias").addEventListener("click", carregarNoticias);

    // Atualiza automaticamente a cada 5 minutos (300.000ms)
    setInterval(carregarNoticias, 300000);
});
