# ProcuraAqui API

API para plataforma de marketing de empreendedores.

## Instalação

```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env com suas credenciais
uvicorn main:app --reload --port 5000
```

## ⚠️ Configuração do Banco de Dados

### Opção 1: Docker (Recomendado)

```bash
# Iniciar PostgreSQL com Docker
docker-compose up -d

# Verificar se está rodando
docker ps
```

### Opção 2: PostgreSQL Local

Se você já tem PostgreSQL instalado localmente, configure o `.env`:

```env
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/nome_do_banco
```

**Nota:** A porta padrão do PostgreSQL é **5432**, não 5433.

### Criar o Banco de Dados

```bash
# Se usar PostgreSQL local
createdb monografia

# Ou via psql
psql -U postgres
CREATE DATABASE monografia;
\q
```

## Configuração (.env)

```env
DATABASE_URL=your_db_url
JWT_SECRET_KEY=your_secret_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## Migrações

```bash
alembic upgrade head
```

## Acesso

- **Tutorial:** http://localhost:5000/
- **API Docs:** http://localhost:5000/docs

## Credenciais de Teste

- **Admin:** admindalton@gmail.com / admin
- **Vendedor:** vendedor@gmail.com / vendedor
- **Cliente:** cliente@gmail.com / cliente

## Troubleshooting

### Erro: "Connection refused" na porta 5433

**Solução:**
1. Verifique se o PostgreSQL está rodando: `docker ps` ou `pg_isready`
2. Inicie o Docker: `docker-compose up -d`
3. Ou ajuste a porta no `.env` para 5432 (porta padrão)
