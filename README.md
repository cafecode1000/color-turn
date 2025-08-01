# 🎨 Projeto ColorTurn com FastAPI

Este é um jogo multiplayer baseado em cartas de cores, desenvolvido com **Python** e **FastAPI**, rodando localmente e idealmente hospedado em um VPS com domínio próprio. O objetivo é reproduzir as regras clássicas de jogos como UNO e adicionar funcionalidades modernas, como API REST, WebSockets, e regras personalizadas.

---

## ✨ Novidade!
Agora com **desafio ao +4** implementado corretamente segundo a regra oficial!

---

## 🚀 Tecnologias Utilizadas

- Python 3.13+
- FastAPI
- Uvicorn
- Pydantic
- Git e GitHub
- VSCode
- Swagger UI (para testes da API)
- VPS Ubuntu 22.04 com NGINX (produção futura)

---

## 📁 Estrutura do Projeto

```
color_turn/
│
├── app/
│   ├── main.py         # Entradas da API FastAPI
│   ├── game.py         # Lógica do jogo (Carta, Baralho, Jogador, Jogo)
│   ├── websocket.py    # (em breve) Comunicação em tempo real
│   └── models.py       # Pydantic Models (requests/responses)
│
├── tests/
│   └── test_game.py    # Testes automatizados
│
├── venv/               # Ambiente virtual Python (não enviado ao GitHub)
├── .gitignore          # Ignora venv, __pycache__, etc.
├── requirements.txt    # Dependências (FastAPI, Uvicorn)
└── README.md           # Este arquivo
```

---

## 🧠 Regras do Jogo Implementadas

- Distribuição de 7 cartas por jogador no início
- Alternância de turnos entre os jogadores
- Pilha de descarte com carta topo
- Cartas de ação: `+2`, `pular`, `inverter`, `coringa`, `+4`
- Jogador pode comprar 1 carta ao invés de jogar
- Carta comprada só pode ser usada se compatível, senão perde a vez
- Baralho se recicla automaticamente com a pilha de descarte (exceto carta do topo)
- **Detecção de vitória automática**
- **Dizer "UNO" com 1 carta**
- **Penalidade por esquecer "UNO"**
- **Desafio ao +4 implementado!**

---

## 📡 Rotas da API

- `POST /novo-jogo`
  - Inicia um novo jogo com lista de nomes
- `GET /estado`
  - Exibe cartas de cada jogador, topo da pilha e turno atual
- `POST /jogar/{nome_jogador}`
  - Jogador joga uma carta da mão
- `POST /comprar/{nome_jogador}`
  - Jogador compra uma carta, verifica se pode jogar
- `POST /uno/{nome_jogador}`
  - Jogador declara "UNO" ao ficar com uma única carta
- `POST /desafiar/{nome_jogador}`
  - Jogador desafia o uso do +4 jogado contra ele

---

## 🎯 Regras Especiais

### Regra do "UNO!"

- Se o jogador terminar sua jogada com **1 carta na mão**:
  - Ele deve chamar `POST /uno/{nome_jogador}` antes de jogar.
  - Se **não declarar**, será **penalizado com 2 cartas automaticamente**.
  - Se declarar corretamente, o sistema registra e não aplica penalidade.
  - O atributo `disse_uno` é **resetado automaticamente** ao final de cada jogada.

### Regra do Desafio ao +4

- Se um jogador jogar um **+4**, o próximo pode chamar:
  - `POST /desafiar/{nome_jogador}`
- O sistema verifica se quem jogou o +4 **tinha cartas da cor que estava em jogo antes da jogada** (e **não da cor escolhida**):
  - Se **sim**: desafio válido → quem jogou compra 4 cartas.
  - Se **não**: desafio falha → desafiante compra 6 cartas.
- Se ninguém desafiar, o próximo jogador deve aceitar o +4 normalmente.

---

## 🛠️ Melhorias Futuras

- Transformar em **jogo multiplayer real com WebSockets**
- Criar frontend em HTML ou React para visualização em tempo real
- Persistência com banco de dados para partidas

---

## ▶️ Como Rodar Localmente

```bash
git clone https://github.com/cafecode1000/uno-game.git
cd uno_game
python -m venv venv
venv\Scripts\activate     # No Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abra no navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ☕ Desenvolvido por Júnior (cafecode.com.br)

Este projeto é inspirado nas regras públicas do jogo de cartas UNO, mas não utiliza material oficial da Mattel.

Em constante evolução e com espírito de aprendizado e diversão.
