let ws;
let jogadorLocal = null;

function connectWs() {
  ws = new WebSocket("ws://" + location.host + "/ws");

  ws.onopen = () => {
    console.log("✅ WebSocket conectado");
    jogadorLocal = prompt("Informe seu nome de jogador (ex: a ou b):").trim().toLowerCase();
    console.log("🔍 Jogador local:", jogadorLocal);
  };

  ws.onclose = () => {
    console.log("❌ WebSocket desconectado");
  };

  ws.onmessage = function (event) {
    const log = document.getElementById("mensagens");
    log.textContent += event.data + "\n";

    console.log("📨 Mensagem recebida:", event.data);
    console.log("🧾 Comparando com jogador local:", jogadorLocal);

    if (event.data.includes("pode desafiar")) {
      if (event.data.includes(jogadorLocal)) {
        console.log("🎯 Exibindo botões de desafio");
        document.getElementById("desafio").style.display = "block";
      } else {
        console.log("⛔ Não é o jogador local que pode desafiar");
      }
    }
  };
}

function desafiar() {
  console.log("🚀 Enviando desafio para /desafiar/" + jogadorLocal);
  fetch("/desafiar/" + jogadorLocal, { method: "POST" })
    .then(resp => resp.json())
    .then(data => {
      console.log("✅ Resposta do desafio:", data);
      document.getElementById("desafio").style.display = "none";
    });
}

function naoDesafiar() {
  console.log("🚫 Enviando decisão para /nao-desafiar/" + jogadorLocal);
  fetch("/nao-desafiar/" + jogadorLocal, { method: "POST" })
    .then(resp => resp.json())
    .then(data => {
      console.log("📦 Resposta de não desafio:", data);
      document.getElementById("desafio").style.display = "none";
    });
}
