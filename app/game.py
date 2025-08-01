import random

class Carta:
    def __init__(self, cor: str, valor: str):
        self.cor = cor  # "vermelho", "azul", "verde", "amarelo", "preto" (wild)
        self.valor = valor  # "0-9", "pular", "inverter", "+2", "coringa", "+4"

    def __repr__(self):
        return f"{self.cor.capitalize()} {self.valor}"


class Baralho:
    CORES = ["vermelho", "azul", "verde", "amarelo"]
    VALORES = [str(i) for i in range(10)] + ["pular", "inverter", "+2"]

    def __init__(self):
        self.cartas = self._gerar_baralho()
        self.embaralhar()

    def _gerar_baralho(self):
        cartas = []
        for cor in self.CORES:
            cartas.append(Carta(cor, "0"))
            for valor in self.VALORES[1:]:
                cartas.append(Carta(cor, valor))
                cartas.append(Carta(cor, valor))
        for _ in range(4):
            cartas.append(Carta("preto", "coringa"))
            cartas.append(Carta("preto", "+4"))
        return cartas

    def embaralhar(self):
        random.shuffle(self.cartas)

    def comprar(self):
        return self.cartas.pop() if self.cartas else None


class Jogador:
    def __init__(self, nome: str):
        self.nome = nome
        self.mao = []
        self.disse_uno = False  # Novo atributo para rastrear se declarou "UNO!"

    def comprar_carta(self, baralho: Baralho, qtd=1):
        cartas_compradas = []
        for _ in range(qtd):
            carta = baralho.comprar()
            if carta:
                self.mao.append(carta)
                cartas_compradas.append(carta)
        return cartas_compradas


    def jogar_carta(self, indice: int):
        if 0 <= indice < len(self.mao):
            return self.mao.pop(indice)
        return None

    def __repr__(self):
        return f"Jogador({self.nome}, Cartas: {len(self.mao)})"


class JogoUNO:
    def __init__(self, nomes_jogadores):
        self.baralho = Baralho()
        self.jogadores = [Jogador(nome) for nome in nomes_jogadores]
        self.pilha_descarte = []
        self.direcao = 1  # 1 = horário, -1 = anti-horário
        self.turno_atual = 0
        self.ultimo_desafio = None  # Guarda info temporária de desafio ao +4


        # Distribuir 7 cartas a cada jogador
        for jogador in self.jogadores:
            jogador.comprar_carta(self.baralho, qtd=7)

        # Iniciar a pilha de descarte
        primeira_carta = self.baralho.comprar()
        while primeira_carta.cor == "preto":  # Evitar iniciar com coringa
            self.baralho.embaralhar()
            primeira_carta = self.baralho.comprar()
        self.pilha_descarte.append(primeira_carta)

    def jogador_atual(self):
        return self.jogadores[self.turno_atual]

    def proximo_turno(self):
        self.turno_atual = (self.turno_atual + self.direcao) % len(self.jogadores)

    def __repr__(self):
        return f"JogoUNO(Turno de {self.jogador_atual().nome}, Topo: {self.pilha_descarte[-1]})"

    def reciclar_pilha(self):
        if len(self.pilha_descarte) <= 1:
            return False  # Nada para reciclar

        topo = self.pilha_descarte[-1]
        recicladas = self.pilha_descarte[:-1]
        random.shuffle(recicladas)

        self.baralho.cartas = recicladas
        self.pilha_descarte = [topo]
        return True

    def registrar_desafio_mais_quatro(self, jogador_que_jogou, vitima):
        self.ultimo_desafio = {
            "jogador_que_jogou": jogador_que_jogou,
            "vitima": vitima,
            "mao_antes": list(jogador_que_jogou.mao)  # cópia da mão antes da jogada
        }
