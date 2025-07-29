from fastapi import FastAPI
from app.game import JogoUNO

app = FastAPI(title="UNO Game API", version="0.1.0")

# Guardar o jogo atual (temporário - depois usaremos algo mais robusto)
jogo_atual = None

@app.post("/novo-jogo")
def novo_jogo(jogadores: list[str]):
    global jogo_atual
    jogo_atual = JogoUNO(jogadores)
    return {"mensagem": "Jogo iniciado!", "topo": str(jogo_atual.pilha_descarte[-1])}

@app.get("/estado")
def estado():
    if not jogo_atual:
        return {"erro": "Nenhum jogo em andamento"}
    return {
        "turno": jogo_atual.jogador_atual().nome,
        "topo": str(jogo_atual.pilha_descarte[-1]),
        "jogadores": {
            j.nome: [str(c) for c in j.mao] for j in jogo_atual.jogadores
        }
    }

from fastapi import HTTPException

@app.post("/comprar/{nome_jogador}")
def comprar_carta(nome_jogador: str):
    if not jogo_atual:
        raise HTTPException(status_code=400, detail="Nenhum jogo em andamento")

    # Encontrar jogador pelo nome
    jogador = next((j for j in jogo_atual.jogadores if j.nome == nome_jogador), None)
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    # Jogador compra 1 carta
    jogador.comprar_carta(jogo_atual.baralho, qtd=1)
    return {
        "mensagem": f"{nome_jogador} comprou uma carta",
        "mao": [str(c) for c in jogador.mao],
        "cartas_restantes_baralho": len(jogo_atual.baralho.cartas)
    }
