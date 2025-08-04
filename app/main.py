from fastapi import FastAPI, HTTPException
from app.game import JogoUNO, Carta
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket import manager
from pydantic import BaseModel

app = FastAPI(title="UNO Game API", version="0.1.0")

# Guardar o jogo atual (temporário - depois usaremos algo mais robusto)
jogo_atual = None

@app.post("/novo-jogo")
def novo_jogo(jogadores: list[str]):
    global jogo_atual
    jogo_atual = JogoUNO(jogadores)
    return {"mensagem": "Jogo iniciado!", "topo": str(jogo_atual.pilha_descarte[-1])}


@app.post("/comprar/{nome_jogador}")
async def comprar_carta(nome_jogador: str):
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

    jogo_atual.registrar_log(
        acao="comprar",
        jogador=nome_jogador,
        detalhes={
            "carta_comprada": str(carta) if carta else "Nenhuma",
            "pode_jogar": pode_jogar,
            "mao_apos": [str(c) for c in jogador.mao],
            "proximo_jogador": jogo_atual.jogador_atual().nome
        }
    )

    await manager.enviar_mensagem(
        f"📥 {nome_jogador} comprou uma carta" +
        (" e passou a vez" if not pode_jogar else " e pode jogar")
    )

    return {
        "mensagem": mensagem,
        "carta_comprada": str(carta) if carta else "Nenhuma",
        "pode_jogar": pode_jogar,
        "mao": [str(c) for c in jogador.mao],
        "proximo_jogador": jogo_atual.jogador_atual().nome if not pode_jogar else nome_jogador
    }


class JogarCartaRequest(BaseModel):
    indice: int  # posição da carta na mão
    nova_cor: str | None = None  # usada apenas para cartas coringa
    

app = FastAPI(title="UNO Game API", version="0.1.0")

jogo_atual = None


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

    jogo_atual.registrar_log(
        acao="comprar",
        jogador=nome_jogador,
        detalhes={
            "carta_comprada": str(carta) if carta else "Nenhuma",
            "pode_jogar": pode_jogar,
            "mao_apos": [str(c) for c in jogador.mao],
            "proximo_jogador": jogo_atual.jogador_atual().nome
        }
    )

    return {
        "mensagem": mensagem,
        "carta_comprada": str(carta) if carta else "Nenhuma",
        "pode_jogar": pode_jogar,
        "mao": [str(c) for c in jogador.mao],
        "proximo_jogador": jogo_atual.jogador_atual().nome if not pode_jogar else nome_jogador
    }

class JogarCartaRequest(BaseModel):
    indice: int
    nova_cor: str | None = None


@app.post("/jogar/{nome_jogador}")
async def jogar_carta(nome_jogador: str, jogada: JogarCartaRequest):
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

    if carta_jogada.valor not in ["coringa", "+4"] and carta_jogada.cor != carta_topo.cor and carta_jogada.valor != carta_topo.valor:
        raise HTTPException(status_code=400, detail=f"Carta '{carta_jogada}' não pode ser jogada sobre '{carta_topo}'")

    # <--- Captura a quantidade de cartas antes da jogada
    tamanho_mao_antes = len(jogador.mao)

    carta_removida = jogador.jogar_carta(jogada.indice)
    mensagem_uno = None
    mensagem_extra = None

    if carta_removida.valor == "+2":
        jogo_atual.pilha_descarte.append(carta_removida)
        jogo_atual.proximo_turno()
        vitima = jogo_atual.jogador_atual()
        vitima.comprar_carta(jogo_atual.baralho, qtd=2)
        mensagem_extra = f"{vitima.nome} comprou 2 cartas e perdeu a vez"
        jogo_atual.proximo_turno()

    elif carta_removida.valor == "pular":
        jogo_atual.pilha_descarte.append(carta_removida)
        vitima_index = (jogo_atual.turno_atual + jogo_atual.direcao) % len(jogo_atual.jogadores)
        vitima = jogo_atual.jogadores[vitima_index]
        mensagem_extra = f"{vitima.nome} perdeu a vez"
        jogo_atual.proximo_turno()
        jogo_atual.proximo_turno()

    elif carta_removida.valor == "inverter":
        jogo_atual.pilha_descarte.append(carta_removida)
        jogo_atual.direcao *= -1
        mensagem_extra = "Direção do jogo invertida"
        if len(jogo_atual.jogadores) == 2:
            jogo_atual.proximo_turno()
        jogo_atual.proximo_turno()

    elif carta_removida.valor == "coringa":
        if not jogada.nova_cor or jogada.nova_cor.lower() not in ["vermelho", "azul", "verde", "amarelo"]:
            raise HTTPException(status_code=400, detail="Cor inválida. Escolha entre: vermelho, azul, verde, amarelo.")

        carta_coringa = Carta(jogada.nova_cor.lower(), carta_removida.valor)
        jogo_atual.pilha_descarte.append(carta_coringa)
        mensagem_extra = f"Cor escolhida: {carta_coringa.cor.capitalize()}"
        jogo_atual.proximo_turno()

    elif carta_removida.valor == "+4":
        if not jogada.nova_cor or jogada.nova_cor.lower() not in ["vermelho", "azul", "verde", "amarelo"]:
            raise HTTPException(status_code=400, detail="Cor inválida. Escolha entre: vermelho, azul, verde, amarelo.")

        carta_especial = Carta(jogada.nova_cor.lower(), carta_removida.valor)
        jogo_atual.pilha_descarte.append(carta_especial)

        proxima_vitima = (jogo_atual.turno_atual + jogo_atual.direcao) % len(jogo_atual.jogadores)
        vitima = jogo_atual.jogadores[proxima_vitima]

        jogo_atual.registrar_desafio_mais_quatro(jogador, vitima, cor_pilha_anterior=carta_topo.cor)
        mensagem_extra = f"{vitima.nome} pode desafiar o +4. Cor escolhida: {carta_especial.cor.capitalize()}"

    else:
        jogo_atual.pilha_descarte.append(carta_removida)
        jogo_atual.proximo_turno()

    for j in jogo_atual.jogadores:
        j.disse_uno = False

    if len(jogador.mao) == 0:
        return {
            "mensagem": f"{jogador.nome} venceu o jogo!",
            "vencedor": jogador.nome
        }

    # ✅ Penalidade só se veio de 2 cartas e ficou com 1
    if tamanho_mao_antes == 2 and len(jogador.mao) == 1 and carta_removida.valor not in ["+4", "coringa"]:
        if not jogador.disse_uno:
            cartas_penalidade = jogador.comprar_carta(jogo_atual.baralho, qtd=2)
            mensagem_uno = f"{jogador.nome} esqueceu de dizer UNO! Comprou 2 cartas como penalidade."
        else:
            mensagem_uno = f"{jogador.nome} declarou UNO corretamente!"

    resposta = {
        "mensagem": f"{nome_jogador} jogou {carta_removida}",
        "novo_topo": str(jogo_atual.pilha_descarte[-1]),
        "proximo_jogador": jogo_atual.jogador_atual().nome,
        "efeito": mensagem_extra
    }

    if mensagem_uno:
        resposta["uno"] = mensagem_uno

    jogo_atual.registrar_log(
        acao="jogar",
        jogador=nome_jogador,
        detalhes={
            "carta_jogada": str(carta_removida),
            "efeito": mensagem_extra,
            "mao_apos": [str(c) for c in jogador.mao],
            "uno": mensagem_uno,
            "proximo_jogador": jogo_atual.jogador_atual().nome
        }
    )

     # Enviar notificação via WebSocket
    print("🔈 Enviando WS:", f"{nome_jogador} jogou {carta_removida}")
    # Enviar notificação via WebSocket
    await manager.enviar_mensagem(
        f"🎮 {nome_jogador} jogou {carta_removida}" +
        (f"\n⚠️ {mensagem_uno}" if mensagem_uno else "") +
        (f"\n🎯 {mensagem_extra}" if mensagem_extra else "")
    )

    return resposta


@app.post("/uno/{nome_jogador}")
async def declarar_uno(nome_jogador: str):
    if not jogo_atual:
        raise HTTPException(status_code=400, detail="Nenhum jogo em andamento")

    jogador = next((j for j in jogo_atual.jogadores if j.nome == nome_jogador), None)
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    if len(jogador.mao) != 1:
        raise HTTPException(status_code=400, detail="Você só pode declarar UNO quando tiver exatamente 1 carta")

    jogador.disse_uno = True
    await manager.enviar_mensagem(f"📢 {jogador.nome} declarou UNO!")
    return {"message": f"{jogador.nome} declarou UNO!"}


# NOVA ROTA: desafio ao +4
@app.post("/desafiar/{nome_jogador}")
async def desafiar_mais_quatro(nome_jogador: str):
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

    jogo_atual.registrar_desafio(
        desafiador=nome_jogador,
        resultado=resultado,
        cartas_compradas=4 if tinha_cor else 6
    )

    await manager.enviar_mensagem(f"⚖️ Desafio ao +4: {resultado}")
    return {"resultado": resultado, "proximo_jogador": jogo_atual.jogador_atual().nome}


@app.get("/historico")
def ver_historico():
    if not jogo_atual:
        raise HTTPException(status_code=400, detail="Nenhum jogo em andamento")
    return jogo_atual.historico


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.conectar(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.enviar_mensagem(f"📢 Jogador disse: {data}")
    except WebSocketDisconnect:
        manager.desconectar(websocket)
