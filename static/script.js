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
    console.log("🤖 Comparando com jogador local:", jogadorLocal);

    if (event.data.includes("pode desafiar")) {
      const match = event.data.match(/(\w+) pode desafiar/);
      console.log("🎯 Detectado possível alvo de desafio:", match ? match[1] : "nenhum");
      console.log("🤖 Comparando com jogador local:", jogadorLocal);

      if (match && match[1].trim().toLowerCase() === jogadorLocal.trim().toLowerCase()) {
        console.log("✅ Jogador é o alvo! Exibindo botões...");
        document.getElementById("desafio").style.display = "block";
      } else {
        console.log("⛔ Outro jogador deve decidir sobre o desafio.");
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