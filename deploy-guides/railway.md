# 🚂 Guia de Deploy - Railway

Deploy do Nazuna Panel no Railway (plataforma moderna e fácil).

## 📋 Pré-requisitos

- Conta no [Railway](https://railway.app)
- Repositório Git (GitHub, GitLab, etc.)
- Código do Nazuna Panel

## 🚀 Deploy Automático (Recomendado)

### Passo 1: Conectar repositório

1. Acesse [Railway](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha o repositório do Nazuna Panel

### Passo 2: Configurar variáveis

No painel do Railway:

```bash
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=production
NODE_ENV=production
PORT=5000
PYTHONPATH=/app/src
```

### Passo 3: Deploy automático

O Railway detecta automaticamente:
- ✅ Python (requirements.txt)
- ✅ Node.js (package.json)
- ✅ Porta automática
- ✅ Build automático

## 🔧 Deploy Manual (CLI)

### Instalar Railway CLI

```bash
# macOS
brew install railway

# Windows (PowerShell)
iwr https://install.railway.app -useb | iex

# Linux
curl -fsSL https://railway.app/install.sh | sh
```

### Deploy via CLI

```bash
# Login
railway login

# Inicializar projeto
railway init

# Deploy
railway up

# Ver logs
railway logs
```

## 📁 Configuração do Projeto

### railway.json

Crie o arquivo `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python src/main.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### nixpacks.toml

Para configuração avançada:

```toml
[phases.setup]
nixPkgs = ['python311', 'nodejs-18_x', 'npm-9_x']

[phases.install]
cmds = [
    'pip install -r requirements.txt',
    'npm install'
]

[phases.build]
cmds = ['echo "Build completed"']

[start]
cmd = 'python src/main.py'
```

## 🗄️ Banco de Dados

### PostgreSQL

```bash
# Adicionar PostgreSQL
railway add postgresql

# A variável DATABASE_URL é criada automaticamente
```

### Redis

```bash
# Adicionar Redis
railway add redis

# A variável REDIS_URL é criada automaticamente
```

### Configurar no código

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Railway usa postgresql:// mas SQLAlchemy precisa de postgresql://
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///app.db'
```

## 🌐 Domínio Customizado

### Configurar domínio

1. No painel Railway, vá em "Settings"
2. Clique em "Domains"
3. Adicione seu domínio
4. Configure DNS:

```
CNAME: seu-dominio.com -> seu-app.railway.app
```

### SSL automático

O Railway fornece SSL automático para todos os domínios.

## 📊 Monitoramento

### Logs em tempo real

```bash
# Via CLI
railway logs

# Via web
# Acesse o painel e clique em "Logs"
```

### Métricas

No painel web você pode ver:
- 📈 CPU usage
- 💾 Memory usage
- 🌐 Network traffic
- 📊 Response times

## 🔄 CI/CD Automático

### GitHub Actions

O Railway se integra automaticamente com GitHub:

1. **Push para main** → Deploy automático
2. **Pull Request** → Preview deploy
3. **Merge** → Deploy para produção

### Configurar branch específica

```bash
# Configurar branch de produção
railway environment production
railway link
```

## 💰 Planos e Preços

### Plano Gratuito (Hobby)

- ✅ $5 de crédito/mês
- ✅ 500 horas de execução
- ✅ 1GB RAM
- ✅ 1GB storage
- ✅ SSL automático
- ✅ Domínio customizado

### Plano Pro

- 💰 $20/mês
- ✅ Recursos ilimitados
- ✅ Prioridade no suporte
- ✅ Métricas avançadas

## 🔧 Configurações Avançadas

### Variáveis de ambiente

```bash
# Via CLI
railway variables set SECRET_KEY=sua-chave

# Via web interface
# Settings → Variables
```

### Configurar região

```bash
# Listar regiões
railway regions

# Configurar região
railway region set us-west1
```

### Configurar recursos

No arquivo `railway.json`:

```json
{
  "deploy": {
    "startCommand": "python src/main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 🛠️ Solução de Problemas

### Build falha

```bash
# Ver logs de build
railway logs --build

# Limpar cache
railway service delete
railway init
```

### App não responde

```bash
# Verificar logs
railway logs

# Verificar variáveis
railway variables

# Reiniciar
railway service restart
```

### Problemas de dependências

Certifique-se que o `requirements.txt` está correto:

```txt
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SocketIO==5.3.6
python-socketio==5.8.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
redis==4.6.0
```

## 🔒 Segurança

### Variáveis sensíveis

```bash
# Gerar chave secreta
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Configurar ambiente
railway variables set FLASK_ENV=production
railway variables set DEBUG=False
```

### Whitelist de IPs

No Railway Pro, você pode configurar:
- 🔒 IP whitelisting
- 🛡️ WAF (Web Application Firewall)
- 🔐 Private networking

## 📱 Integração com Frontend

### Servir frontend estático

```python
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

### Build do frontend

Adicione ao `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "phases": {
    "build": {
      "cmds": [
        "cd frontend && npm install && npm run build",
        "cp -r frontend/dist/* static/"
      ]
    }
  }
}
```

## 🔄 Backup e Restore

### Backup do banco

```bash
# Conectar ao banco
railway connect postgresql

# Fazer backup
pg_dump $DATABASE_URL > backup.sql

# Restaurar
psql $DATABASE_URL < backup.sql
```

### Backup de arquivos

```python
# Implementar endpoint de backup
@app.route('/api/backup')
def create_backup():
    # Lógica de backup
    pass
```

## 🚀 Performance

### Otimizações

1. **Gunicorn** para produção:

```python
# gunicorn_config.py
bind = "0.0.0.0:5000"
workers = 2
worker_class = "eventlet"
worker_connections = 1000
```

2. **Caching** com Redis:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

3. **Compressão**:

```python
from flask_compress import Compress

Compress(app)
```

## 📞 Suporte

### Recursos úteis

- 📚 [Documentação](https://docs.railway.app/)
- 💬 [Discord](https://discord.gg/railway)
- 🐛 [GitHub Issues](https://github.com/railwayapp/railway/issues)
- 📧 Email: help@railway.app

### Comandos úteis

```bash
# Status do projeto
railway status

# Conectar ao banco
railway connect postgresql

# Shell no container
railway shell

# Ver variáveis
railway variables

# Logs em tempo real
railway logs --follow
```

## 🔗 Migração de outras plataformas

### Do Heroku

```bash
# Exportar variáveis do Heroku
heroku config -s > .env

# Importar no Railway
railway variables set $(cat .env)
```

### Do Vercel

```bash
# Baixar variáveis
vercel env pull .env

# Importar no Railway
railway variables set $(cat .env)
```

---

**✅ Deploy concluído! Seu Nazuna Panel está rodando no Railway.**

- 🌐 **URL**: `https://seu-projeto.railway.app`
- 📊 **Dashboard**: [railway.app](https://railway.app)
- 📝 **Logs**: `railway logs`

