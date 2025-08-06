# 🃏 Projeto UNO com FastAPI

Este é um jogo UNO multiplayer desenvolvido com **Python** e **FastAPI**, rodando localmente e idealmente hospedado em um VPS com domínio próprio. O objetivo é reproduzir as regras clássicas do UNO e adicionar funcionalidades modernas, como API REST, WebSockets e regras personalizadas.

---

## 🚀 Tecnologias Utilizadas

- Python 3.13+
- FastAPI
- Uvicorn
- WebSockets (via `websockets` ou `uvicorn[standard]`)
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
│   ├── websocket.py    # Comunicação WebSocket em tempo real
│   └── models.py       # Pydantic Models (requests/responses)
│
├── tests/
│   └── test_game.py    # Testes automatizados
│
├── venv/               # Ambiente virtual Python (não enviado ao GitHub)
├── requirements.txt    # Dependências (FastAPI, Uvicorn, websockets)
├── teste_ws.html       # Cliente simples de teste WebSocket
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
- **Penalidade por esquecer "UNO"** (ver detalhes abaixo)
- **Desafio ao +4 com lógica completa e penalidades configuráveis**
- **WebSocket funcional com mensagens em tempo real ampliadas** ✅
- **Botões interativos "Desafiar / Não desafiar" no frontend** ✅

---

## 📡 Rotas da API

- `POST /novo-jogo`  
  Inicia um novo jogo com lista de nomes

- `GET /estado`  
  Exibe cartas de cada jogador, topo da pilha e turno atual

- `POST /jogar/{nome_jogador}`  
  Jogador joga uma carta da mão (notifica via WebSocket)

- `POST /comprar/{nome_jogador}`  
  Jogador compra uma carta, verifica se pode jogar (**também notifica via WebSocket**)

- `POST /uno/{nome_jogador}`  
  Jogador declara "UNO" ao ficar com uma única carta (**também notifica via WebSocket**)

- `POST /desafiar/{nome_jogador}`  
  Jogador desafia o uso do +4 jogado contra ele (**também notifica via WebSocket**)

- `POST /nao-desafiar/{nome_jogador}`  
  Jogador opta por **não desafiar** o +4, recebendo 4 cartas como penalidade

- `GET /historico`  
  Retorna o histórico de ações do jogo

- `GET /ws`  
  **WebSocket para comunicação em tempo real com todos os jogadores**

---

## 📢 Notificações em tempo real (WebSocket)

Agora o jogo envia mensagens automáticas para todos os jogadores conectados via WebSocket:

- Jogadas como: `🎮 b jogou Azul +2`
- Penalidades: `⚠️ a esqueceu de dizer UNO! Comprou 2 cartas como penalidade.`
- Efeitos especiais: `🎯 Direção do jogo invertida`, `🎯 Cor escolhida: Amarelo`
- `📥 Jogador comprou uma carta...`
- `📢 Jogador declarou UNO!`
- ⚖️ Desafio ao +4:
  - Exibe se o desafio foi bem-sucedido ou não
  - Penalidades aplicadas ao jogador correto
  - Mensagem exibida para todos os conectados

---

## 🧪 Interação de desafio ao +4 no navegador

Ao jogar um +4, o jogador afetado verá no navegador:

⚖️ Você deseja desafiar o +4?  
✅ Se sim, o outro jogador pode ser penalizado.  
❌ Se não, você comprará 4 cartas — e continuará o jogo.

Essa decisão é feita através de dois botões que aparecem automaticamente se for sua vez de decidir.

---

## 🎯 Regra do "UNO!"

- Se o jogador terminar sua jogada com **1 carta na mão**:
  - Ele **pode** chamar `POST /uno/{nome_jogador}` **antes do fim de seu turno**
  - Se **não declarar**, será **penalizado com 2 cartas automaticamente**
  - Se declarar corretamente, o sistema registra e não aplica penalidade
  - O atributo `disse_uno` é **resetado automaticamente** ao final da jogada

---

## 🛠️ Melhorias Futuras

- Criar frontend em FastAPI visualização em tempo real
- Persistência com banco de dados para partidas
- Sistema de salas e autenticação de jogadores

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