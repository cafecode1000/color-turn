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

    jogador = next((j for j in jogo_atual.jogadores if j.nome == nome_jogador), None)
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    if jogador != jogo_atual.jogador_atual():
        raise HTTPException(status_code=403, detail="Não é o turno deste jogador")

    cartas = jogador.comprar_carta(jogo_atual.baralho, qtd=1)

    if not cartas:
        reciclou = jogo_atual.reciclar_pilha()
        if reciclou:
            cartas = jogador.comprar_carta(jogo_atual.baralho, qtd=1)
        if not cartas:
            raise HTTPException(status_code=400, detail="Sem cartas no baralho nem na pilha de descarte")

    carta = cartas[0] if cartas else None
    topo = jogo_atual.pilha_descarte[-1]

    pode_jogar = (
        carta and (
            carta.cor == topo.cor or
            carta.valor == topo.valor or
            carta.cor == "preto"
        )
    )

    mensagem = f"{nome_jogador} comprou uma carta"
    if not pode_jogar:
        jogo_atual.proximo_turno()
        mensagem += " e passou a vez"

    return {
        "mensagem": mensagem,
        "carta_comprada": str(carta) if carta else "Nenhuma",
        "pode_jogar": pode_jogar,
        "mao": [str(c) for c in jogador.mao],
        "proximo_jogador": jogo_atual.jogador_atual().nome if not pode_jogar else nome_jogador
    }



from pydantic import BaseModel

class JogarCartaRequest(BaseModel):
    indice: int  # posição da carta na mão
    nova_cor: str | None = None  # usada apenas para cartas coringa
    

@app.post("/jogar/{nome_jogador}")
def jogar_carta(nome_jogador: str, jogada: JogarCartaRequest):
    # Primeiro, verifica se o jogo existe
    if not jogo_atual:
        raise HTTPException(status_code=400, detail="Nenhum jogo em andamento")
    
    # Agora procura o jogador no turno
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
    if carta_jogada.valor not in ["coringa", "+4"] and carta_jogada.cor != carta_topo.cor and carta_jogada.valor != carta_topo.valor:
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
        
        # Atualiza a cor da carta para a escolhida
        carta_removida.cor = jogada.nova_cor.lower()

        mensagem_extra = f"Cor escolhida: {carta_removida.cor.capitalize()}"
        jogo_atual.proximo_turno()
    elif carta_removida.valor == "+4":
        if not jogada.nova_cor or jogada.nova_cor.lower() not in ["vermelho", "azul", "verde", "amarelo"]:
            raise HTTPException(
                status_code=400,
                detail="Cor inválida. Escolha entre: vermelho, azul, verde, amarelo."
            )

        # Define a nova cor na carta
        carta_removida.cor = jogada.nova_cor.lower()

        # Próximo jogador compra 4 cartas e perde a vez
        vitima = jogo_atual.jogador_atual()
        vitima.comprar_carta(jogo_atual.baralho, qtd=4)
        mensagem_extra = f"{vitima.nome} comprou 4 cartas e perdeu a vez. Cor escolhida: {carta_removida.cor.capitalize()}"
        jogo_atual.proximo_turno()

    else:
        mensagem_extra = None
    
    # Verifica a vitória
    if len(jogador.mao) == 0:
        return {
            "mensagem": f"{jogador.nome} venceu o jogo!",
            "vencedor": jogador.nome
        }

    return {
        "mensagem": f"{nome_jogador} jogou {carta_removida}",
        "novo_topo": str(carta_removida),
        "proximo_jogador": jogo_atual.jogador_atual().nome,
        "efeito": mensagem_extra
    }
