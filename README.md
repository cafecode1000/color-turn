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
- **Desafio ao +4 implementado!**
- **WebSocket funcional com mensagens em tempo real**

---

## 📡 Rotas da API

- `POST /novo-jogo`  
  Inicia um novo jogo com lista de nomes

- `GET /estado`  
  Exibe cartas de cada jogador, topo da pilha e turno atual

- `POST /jogar/{nome_jogador}`  
  Jogador joga uma carta da mão (notifica via WebSocket)

- `POST /comprar/{nome_jogador}`  
  Jogador compra uma carta, verifica se pode jogar

- `POST /uno/{nome_jogador}`  
  Jogador declara "UNO" ao ficar com uma única carta

- `POST /desafiar/{nome_jogador}`  
  Jogador desafia o uso do +4 jogado contra ele

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

### ✅ Como testar localmente:

1. Suba o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Abra o arquivo `teste_ws.html` no navegador

3. Faça jogadas usando o Swagger ou outro cliente HTTP

4. Veja os eventos aparecendo em tempo real nas abas conectadas

---

## 🎯 Regra do "UNO!"

- Se o jogador terminar sua jogada com **1 carta na mão**:
  - Ele **pode** chamar `POST /uno/{nome_jogador}` **antes do fim de seu turno** (inclusive após um desafio ao +4).
  - Se **não declarar**, será **penalizado com 2 cartas automaticamente** **apenas após o turno terminar**, desde que não tenha vencido.
  - Se declarar corretamente, o sistema registra e não aplica penalidade.
  - O atributo `disse_uno` é **resetado automaticamente** ao final da jogada.

---

## 🛠️ Melhorias Futuras

- Expandir uso de WebSockets (já integrado à rota `/jogar`) para outras ações como `/uno` e `/desafiar`
- Criar frontend em HTML ou React para visualização em tempo real
- Persistência com banco de dados para partidas
- Sistema de salas e autenticação de jogadores

---

## ▶️ Como Rodar Localmente

```bash
git clone https://github.com/cafecode1000/uno-game.git
cd uno_game
python -m venv venv
venv\Scriptsctivate     # No Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abra no navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ☕ Desenvolvido por Júnior (cafecode.com.br)

Em constante evolução e com espírito de aprendizado e diversão.