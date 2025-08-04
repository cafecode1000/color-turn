from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.ativos: List[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.ativos.append(websocket)

    def desconectar(self, websocket: WebSocket):
        self.ativos.remove(websocket)

    async def enviar_mensagem(self, mensagem: str):
        for conexao in self.ativos:
            await conexao.send_text(mensagem)

manager = ConnectionManager()
