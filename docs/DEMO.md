# 🎤 Guia de Apresentação — BlaBlaIF

Roteiro pratico para demonstrar o BlaBlaIF ao vivo. Siga na ordem.

---

## ✅ Checklist pre-apresentacao (faca 10 min antes)

1. **Suba o backend** (terminal 1):
   ```bash
   cd server
   .venv/bin/uvicorn app.main:app --reload
   ```
   Confirme no navegador: <http://127.0.0.1:8000/docs> abre o Swagger.

2. **Suba o frontend** (terminal 2):
   ```bash
   cd client
   npm run dev
   ```
   Confirme: <http://localhost:3000> carrega a tela inicial com "BlaBlaIF".

3. **Confira que ha dados de demonstracao.** Faca login como `gui@aluno.ifsp.edu.br`
   (`demo1234`) e veja se o painel tem caronas, solicitacoes e o sininho de
   notificacoes com contagem. Se o painel estiver vazio, rode o seeder
   (veja ["Repovoar os dados"](#-repovoar-os-dados-se-o-painel-estiver-vazio)).

> Deixe os **dois terminais abertos** durante a apresentacao. O backend imprime
> cada requisicao — util para mostrar a integracao se quiser.

---

## 🔑 Logins prontos para o demo

Todas as contas de demonstracao usam a senha **`demo1234`**.

| Papel no roteiro | Email | Senha |
|---|---|---|
| **Voce / protagonista** | `gui@aluno.ifsp.edu.br` | `demo1234` |
| Motorista (aceita vagas) | `carla.souza@aluno.ifsp.edu.br` | `demo1234` |
| Passageiro | `bruno.passageiro@aluno.ifsp.edu.br` | `demo1234` |
| Motorista extra | `ana.motorista@aluno.ifsp.edu.br` | `demo1234` |

> A conta **Gui** ja vem com solicitacoes pendentes para aceitar e notificacoes
> no sininho — e a melhor para mostrar o painel "cheio".

---

## 🎬 Roteiro sugerido (~5 min)

1. **Tela inicial e cadastro.** Mostre a landing. Clique em cadastrar e crie um
   aluno com email `@aluno.ifsp.edu.br`. Tente um email fora do dominio para
   mostrar a validacao (so aceita `@aluno.ifsp.edu.br`).
2. **Login.** Entre como `gui@aluno.ifsp.edu.br`.
3. **Caronas disponiveis.** Mostre a lista de caronas semeadas (origem, destino,
   horario, preco por vaga, vagas restantes).
4. **Solicitar vaga.** Em uma carona de outro aluno, peca uma vaga informando o
   endereco de embarque e uma mensagem. Destaque que **o telefone do motorista
   so aparece depois do aceite** (transparencia + privacidade).
5. **Lado motorista.** Abra outra aba/janela anonima e entre como
   `carla.souza@aluno.ifsp.edu.br` (`demo1234`). Em "minhas caronas", **aceite**
   uma solicitacao pendente. Volte como passageiro e mostre o **telefone agora
   visivel**.
6. **Notificacoes.** Mostre o sininho da conta Gui com as notificacoes de
   solicitacao/aceite.

---

## 🔄 Repovoar os dados (se o painel estiver vazio)

O backend cria automaticamente o campus **IFSP Campus Votuporanga** e um seed
minimo (motorista + passageiro + 1 carona) quando o banco esta vazio. Para o
conjunto completo de demonstracao (varias caronas, solicitacoes e notificacoes):

```bash
cd server
.venv/bin/python -m scripts.add_demo_data
```

> As notificacoes e algumas solicitacoes sao direcionadas a conta
> `gui@aluno.ifsp.edu.br`. **Cadastre/entre como Gui pelo menos uma vez antes**
> de rodar o seeder para que esse conteudo apareca no painel dele.

### Resetar do zero
Pare o backend, apague o banco e suba de novo:
```bash
cd server
rm -f blablaif.db
.venv/bin/uvicorn app.main:app --reload   # recria o campus + seed minimo
```
Depois cadastre o Gui e rode `add_demo_data` novamente para o demo completo.

---

## 🛟 Se algo der errado na hora

| Sintoma | Causa provavel | Acao |
|---|---|---|
| `node`/`npm` não encontrado | mise não ativou no terminal | Abra um terminal novo, ou rode `mise exec node@22 -- npm run dev` |
| Popup "Command Line Dev Tools" | venv antigo de outra maquina | Ignore; o `.venv` ja foi recriado com `uv` |
| Frontend abre mas da erro 500 | `node_modules` de outra plataforma | `cd client && rm -rf node_modules && npm install` |
| Porta 8000/3000 ocupada | servidor antigo rodando | Feche o terminal antigo ou mate o processo na porta |
| Painel vazio | banco sem dados | Rode o seeder (secao acima) |

> O backend roda com uma chave de desenvolvimento de fallback, entao **nao
> precisa de `.env`** para o demo local.
