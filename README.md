# ProcuraAqui API

API for entrepreneurs marketing plataform.

## Instalation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn main:app --reload --port 5000
```

## ⚠️ Database Configuration

### Option 1: Docker (Recomended)

```bash
# Start PostgreSQL with Docker
docker-compose up -d

# Verify if it's running
docker ps
```

### Option 2: Local PostgreSQL

If you alread have PostgreSQL installed localy, configure the `.env`:

```env
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_db_name
```

**Note:** The default port of PostgreSQL is **5432**, not 5433.

### Create Database

```bash
# If local PostgreSQL
createdb your_db_name

# Or through psql
psql -U postgres
CREATE DATABASE your_db_name;
\q
```

## Configuration (.env)

```env
DATABASE_URL=your_db_url
JWT_SECRET_KEY=your_secret_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## Migration

```bash
alembic upgrade head
```

## Access

- **Tutorial:** http://localhost:5000/
- **API Docs:** http://localhost:5000/docs

## Test Credentials

- **Admin:** admindalton@gmail.com / admin
- **Vendedor:** vendedor@gmail.com / vendedor
- **Cliente:** cliente@gmail.com / cliente

## Troubleshooting

### Erro: "Connection refused" na porta 5433

**Solution:**
1. Verify if PostgreSQL is running: `docker ps` or `pg_isready`
2. Run Docker: `docker-compose up -d`
3. Or change `.env` port to 5432 (default port)
