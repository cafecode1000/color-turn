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

    # Verifica se o jogador ficou com 1 carta após jogar
    mensagem_uno = None
    if len(jogador.mao) == 1:
        if not jogador.disse_uno:
            # Penalidade por não dizer UNO
            cartas_penalidade = jogo_atual.comprar_cartas(2)
            jogador.mao.extend(cartas_penalidade)
            mensagem_uno = f"{jogador.nome} esqueceu de dizer UNO! Comprou 2 cartas como penalidade."
        else:
            mensagem_uno = f"{jogador.nome} declarou UNO corretamente!"


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

        carta_removida.cor = jogada.nova_cor.lower()

        vitima = jogo_atual.jogador_atual()

        # REGISTRA desafio pendente antes da vítima comprar cartas
        jogo_atual.registrar_desafio_mais_quatro(jogador, vitima, cor_pilha_anterior=carta_topo.cor)
        mensagem_extra = f"{vitima.nome} pode desafiar o +4. Cor escolhida: {carta_removida.cor.capitalize()}"
    else:
        mensagem_extra = None
    
    # Após a jogada, todos os jogadores devem ter 'disse_uno' resetado
    for j in jogo_atual.jogadores:
        j.disse_uno = False

    # Verifica a vitória
    if len(jogador.mao) == 0:
        return {
            "mensagem": f"{jogador.nome} venceu o jogo!",
            "vencedor": jogador.nome
        }

    resposta = {
        "mensagem": f"{nome_jogador} jogou {carta_removida}",
        "novo_topo": str(carta_removida),
        "proximo_jogador": jogo_atual.jogador_atual().nome,
        "efeito": mensagem_extra
    }

    if mensagem_uno:
        resposta["uno"] = mensagem_uno

    return resposta



@app.post("/uno/{nome_jogador}")
def declarar_uno(nome_jogador: str):
    if not jogo_atual:
        raise HTTPException(status_code=400, detail="Nenhum jogo em andamento")

    jogador = next((j for j in jogo_atual.jogadores if j.nome == nome_jogador), None)
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    if len(jogador.mao) != 1:
        raise HTTPException(status_code=400, detail="Você só pode declarar UNO quando tiver exatamente 1 carta")

    jogador.disse_uno = True
    return {"message": f"{jogador.nome} declarou UNO!"}


# NOVA ROTA: desafio ao +4

# NOVA ROTA: desafio ao +4

@app.post("/desafiar/{nome_jogador}")
def desafiar_mais_quatro(nome_jogador: str):
    if not jogo_atual or not jogo_atual.ultimo_desafio:
        raise HTTPException(status_code=400, detail="Nenhum desafio pendente")

    contexto = jogo_atual.ultimo_desafio
    if contexto["vitima"].nome != nome_jogador:
        raise HTTPException(status_code=403, detail="Apenas a vítima do +4 pode desafiar")

    mao_antes = contexto["mao_antes"]
    jogador_que_jogou = contexto["jogador_que_jogou"]
    cor_anterior = contexto["cor_anterior"]

    tinha_cor = any(carta.cor == cor_anterior for carta in mao_antes if carta.cor != "preto")

    if tinha_cor:
        jogador_que_jogou.comprar_carta(jogo_atual.baralho, qtd=4)
        resultado = f"{jogador_que_jogou.nome} tinha a cor {cor_anterior}! Comprou 4 cartas como penalidade."
    else:
        contexto["vitima"].comprar_carta(jogo_atual.baralho, qtd=6)
        resultado = f"Desafio falhou. {nome_jogador} comprou 6 cartas."

    jogo_atual.proximo_turno()
    jogo_atual.ultimo_desafio = None

    return {"resultado": resultado, "proximo_jogador": jogo_atual.jogador_atual().nome}
