# BlaBlaIF 🚗
**Bem-vindo ao BlaBlaIF:** Uma plataforma digital para facilitar a locomoção de alunos do Instituto Federal de São Paulo (IFSP), ajudando na organização de caronas estudantis com segurança e transparência.

## 🎯 Objetivo
O BlaBlaIF busca solucionar desafios logísticos e operacionais enfrentados por estudantes intermunicipais ao se deslocarem para os câmpus do IFSP. Por meio de nosso aplicativo, estudantes que oferecem caronas podem de forma segura se conectar com alunos em busca de locomoção.

O sistema foca em transparência (verificação via credenciais estudantis nativas), agilidade e viés econômico voltado ao universitário, possuindo um modelo de banco de dados capaz de abstrair fluxos entre Alunos, Professores e Corridas vinculadas ao território Campus.

---

## 🛠️ Tecnologias
- **Backend:** FastAPI, Python, SQLAlchemy.
- **Banco de Dados:** SQLite (volátil e de fácil setup para colaboradores locais).
- **Autenticação:** JWT Bearer com Hash `bcrypt`.
- **Testes:** Pytest

---

## 🚀 Como Preparar e Rodar
Para iniciar seu ambiente de desenvolvimento, siga este passo a passo.

### 1. Preparação de Ambiente
Primeiro, crie/ative o ambiente virtual e acesse a pasta `server`:
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuração de Segredos
Crie o seu arquivo de diretrizes ambientais baseado no exemplo de nosso repositório.
**Copie o `.env.example` para formar o `.env` oficial:**
```bash
cp .env.example .env
```
O projeto tambem possui uma chave local de desenvolvimento como fallback, mas o `.env` deve ser usado para configurar ambientes compartilhados.

### 3. Executando Localmente (FastAPI / Uvicorn)
Sempre execute o backend através de Uvicorn apontando para a fundação arquitetônica nativa localizada em `app/main.py`:
```bash
.venv/bin/uvicorn app.main:app --reload
```
A base SQLite (`blablaif.db`) sera criada automaticamente. O V1 cria o campus fixo **IFSP Campus Votuporanga** e alguns dados locais de demonstracao quando a base esta vazia.

Acesse a rica documentação interativa Open API Swagger clicando em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Rodando a Suíte de Automação (Testes)
Quando realizar pull-requests com alterações estruturais no código, rode a bateria integral para conferir a compatibilidade. Nosso Pytest simula um SQLite isolado não sujando sua base de testes manuais originais:
```bash
.venv/bin/python -m pytest
```

### 5. Frontend (Next.js)
Em outro terminal:
```bash
cd client
npm install
npm run dev
```
O frontend usa `NEXT_PUBLIC_API_URL` quando definido; caso contrario, chama `http://127.0.0.1:8000/api/v1`.

---

## ✅ Escopo V1
- Cadastro/login com email `@aluno.ifsp.edu.br`.
- Painel unico autenticado para caronas disponiveis, minhas caronas e minhas solicitacoes.
- Criacao de carona com preco manual por vaga.
- Solicitacao de vaga com endereco de embarque e mensagem opcional.
- Aceite/recusa pelo motorista e cancelamento minimo.
- Telefones visiveis somente apos aceite.

Veja [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) para itens planejados fora do V1.

---

## 🏗️ Estrutura do Padrão Back-End
```
server/
├── app/
│   ├── api/             # Rotas de acesso ao ecossistema
│   ├── core/            # Configuração e Segurança 
│   ├── db/              # Parametrizações do Banco Relacional
│   ├── models/          # SQLAlchemy Entities
│   ├── schemas/         # Pydantic Typing e Validações
│   └── main.py          # Entrypoint do Backend Integrado
├── tests/               # Ambientes Unificados de Pytest Integrations
```
