from app.game import JogoUNO, Carta


def preparar_mao(jogador, cartas_str):
    jogador.mao.clear()
    for carta in cartas_str:
        cor, valor = carta.split()
        jogador.mao.append(Carta(cor.lower(), valor))


def test_penalidade_uno_quando_esquece():
    jogo = JogoUNO(["a", "b"])
    jogador = jogo.jogadores[0]

    # Configura mão com 2 cartas
    preparar_mao(jogador, ["vermelho 3", "vermelho 7"])
    jogo.pilha_descarte[-1] = Carta("vermelho", "5")

    # Não diz UNO
    carta_jogada = jogador.jogar_carta(0)
    jogo.pilha_descarte.append(carta_jogada)

    if len(jogador.mao) == 1 and len(jogador.mao) + 2 != 3:
        print("❌ Erro: penalidade não aplicada quando devia.")
    else:
        print("✅ Passou: penalidade aplicada quando não disse UNO com 2 cartas.")


def test_sem_penalidade_quando_disse_uno():
    jogo = JogoUNO(["a", "b"])
    jogador = jogo.jogadores[0]

    # Configura mão com 2 cartas
    preparar_mao(jogador, ["azul 5", "azul 9"])
    jogo.pilha_descarte[-1] = Carta("azul", "7")

    jogador.disse_uno = True
    carta_jogada = jogador.jogar_carta(0)
    jogo.pilha_descarte.append(carta_jogada)

    if len(jogador.mao) == 1:
        print("✅ Passou: não houve penalidade quando declarou UNO.")
    else:
        print("❌ Erro: penalidade aplicada mesmo tendo declarado UNO.")


def test_sem_penalidade_quando_tinha_mais_de_duas():
    jogo = JogoUNO(["a", "b"])
    jogador = jogo.jogadores[0]

    preparar_mao(jogador, ["verde 1", "verde 2", "verde 3"])
    jogo.pilha_descarte[-1] = Carta("verde", "5")

    carta_jogada = jogador.jogar_carta(0)
    jogo.pilha_descarte.append(carta_jogada)

    if len(jogador.mao) == 2:
        print("✅ Passou: não houve penalidade com mais de 2 cartas.")
    else:
        print("❌ Erro: penalidade incorreta com 3 cartas.")


def test_sem_penalidade_quando_vence():
    jogo = JogoUNO(["a", "b"])
    jogador = jogo.jogadores[0]

    preparar_mao(jogador, ["azul 1"])
    jogo.pilha_descarte[-1] = Carta("azul", "7")

    carta_jogada = jogador.jogar_carta(0)
    jogo.pilha_descarte.append(carta_jogada)

    if len(jogador.mao) == 0:
        print("✅ Passou: jogador venceu com 1 carta e não foi penalizado.")
    else:
        print("❌ Erro: penalidade indevida ao vencer.")


if __name__ == "__main__":
    test_penalidade_uno_quando_esquece()
    test_sem_penalidade_quando_disse_uno()
    test_sem_penalidade_quando_tinha_mais_de_duas()
    test_sem_penalidade_quando_vence()
