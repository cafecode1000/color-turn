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

from pydantic import BaseModel

class JogarCartaRequest(BaseModel):
    indice: int  # posição da carta na mão
    nova_cor: str | None = None  # usada apenas para cartas coringa

@app.post("/jogar/{nome_jogador}")
def jogar_carta(nome_jogador: str, jogada: JogarCartaRequest):
    if not jogo_atual:
        raise HTTPException(status_code=400, detail="Nenhum jogo em andamento")

    jogador = next((j for j in jogo_atual.jogadores if j.nome == nome_jogador), None)
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    if jogador != jogo_atual.jogador_atual():
        raise HTTPException(status_code=403, detail="Não é o turno deste jogador")

    if jogada.indice < 0 or jogada.indice >= len(jogador.mao):
        raise HTTPException(status_code=400, detail="Índice de carta inválido")

    carta_jogada = jogador.mao[jogada.indice]
    carta_topo = jogo_atual.pilha_descarte[-1]

    # Validação básica: mesma cor ou mesmo valor
    if carta_jogada.valor != "coringa" and carta_jogada.cor != carta_topo.cor and carta_jogada.valor != carta_topo.valor:
        raise HTTPException(status_code=400, detail=f"Carta '{carta_jogada}' não pode ser jogada sobre '{carta_topo}'")

    # Joga a carta
    carta_removida = jogador.jogar_carta(jogada.indice)
    jogo_atual.pilha_descarte.append(carta_removida)

    # Avança o turno normalmente
    jogo_atual.proximo_turno()

    # Se for +2, próximo jogador compra duas cartas e perde a vez
    if carta_removida.valor == "+2":
        vitima = jogo_atual.jogador_atual()
        vitima.comprar_carta(jogo_atual.baralho, qtd=2)
        mensagem_extra = f"{vitima.nome} comprou 2 cartas e perdeu a vez"
        jogo_atual.proximo_turno()
    elif carta_removida.valor == "pular":
        vitima = jogo_atual.jogador_atual()
        mensagem_extra = f"{vitima.nome} perdeu a vez"
        jogo_atual.proximo_turno()
    elif carta_removida.valor == "inverter":
        jogo_atual.direcao *= -1
        mensagem_extra = "Direção do jogo invertida"
        jogo_atual.proximo_turno()
    elif carta_removida.valor == "coringa":
        if not jogada.nova_cor or jogada.nova_cor.lower() not in ["vermelho", "azul", "verde", "amarelo"]:
            raise HTTPException(status_code=400, detail="Cor inválida. Escolha entre: vermelho, azul, verde, amarelo.")
        
        # Trocar temporariamente a cor da carta coringa
        carta_removida.cor = jogada.nova_cor.lower()
        mensagem_extra = f"Cor escolhida: {carta_removida.cor.capitalize()}"
        jogo_atual.proximo_turno()
    else:
        mensagem_extra = None


    return {
        "mensagem": f"{nome_jogador} jogou {carta_removida}",
        "novo_topo": str(carta_removida),
        "proximo_jogador": jogo_atual.jogador_atual().nome,
        "efeito": mensagem_extra
    }
