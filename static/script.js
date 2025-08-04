let ws;

function connectWs() {
  ws = new WebSocket("ws://" + location.host + "/ws");

  ws.onmessage = function (event) {
    const log = document.getElementById("mensagens");
    log.textContent += event.data + "\\n";
  };

  ws.onopen = () => console.log("✅ Conectado ao WebSocket");
  ws.onclose = () => console.log("❌ WebSocket fechado");
}
