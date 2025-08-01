# 🃏 Projeto UNO com FastAPI

Este é um jogo UNO multiplayer desenvolvido com **Python** e **FastAPI**, rodando localmente e idealmente hospedado em um VPS com domínio próprio. O objetivo é reproduzir as regras clássicas do UNO e adicionar funcionalidades modernas, como API REST, WebSockets, e regras personalizadas.

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
uno_game/
│
├── app/
│   ├── main.py         # Entradas da API FastAPI
│   ├── game.py         # Lógica do UNO (Carta, Baralho, Jogador, JogoUNO)
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
- **Desafio +4** (em breve)
- **Dizer "UNO" com 1 carta** (em breve)
- **Penalidade por esquecer "UNO"** (em breve)

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

---

## 🛠️ Melhorias Futuras

- Implementar **desafio ao +4**
- Adicionar opção para o jogador dizer `"UNO"`
- Penalizar quem esquecer de dizer "UNO"
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

Em constante evolução e com espírito de aprendizado e diversão.
