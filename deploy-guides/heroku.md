# ☁️ Guia de Deploy - Heroku

Deploy do Nazuna Panel no Heroku (gratuito com limitações).

## 📋 Pré-requisitos

- Conta no [Heroku](https://heroku.com)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado
- Git instalado

## 🚀 Deploy Rápido

### Passo 1: Preparar o projeto

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/nazuna-panel.git
cd nazuna-panel

# Fazer login no Heroku
heroku login
```

### Passo 2: Criar app no Heroku

```bash
# Criar app (nome único)
heroku create seu-app-nazuna

# Ou usar nome automático
heroku create
```

### Passo 3: Configurar variáveis de ambiente

```bash
heroku config:set SECRET_KEY="sua-chave-secreta-aqui"
heroku config:set FLASK_ENV="production"
heroku config:set NODE_ENV="production"
heroku config:set PORT="5000"
```

### Passo 4: Adicionar buildpacks

```bash
# Python buildpack
heroku buildpacks:add heroku/python

# Node.js buildpack (para o bot)
heroku buildpacks:add heroku/nodejs
```

### Passo 5: Deploy

```bash
git push heroku main
```

### Passo 6: Verificar deploy

```bash
# Ver logs
heroku logs --tail

# Abrir app
heroku open
```

## 📁 Arquivos Necessários

### Procfile

Crie o arquivo `Procfile` na raiz:

```
web: python src/main.py
```

### runtime.txt

Crie o arquivo `runtime.txt`:

```
python-3.11.0
```

### package.json (para Node.js)

```json
{
  "name": "nazuna-panel",
  "version": "1.0.0",
  "engines": {
    "node": "18.x",
    "npm": "9.x"
  },
  "scripts": {
    "build": "echo 'Build completed'",
    "start": "echo 'App started'"
  },
  "dependencies": {}
}
```

### requirements.txt

Certifique-se que está atualizado:

```
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SocketIO==5.3.6
python-socketio==5.8.0
gunicorn==21.2.0
```

## ⚙️ Configuração Avançada

### Usar PostgreSQL (recomendado)

```bash
# Adicionar addon PostgreSQL
heroku addons:create heroku-postgresql:mini

# Verificar URL do banco
heroku config:get DATABASE_URL
```

Atualizar `src/config.py`:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Usar Redis para WebSocket

```bash
# Adicionar Redis
heroku addons:create heroku-redis:mini

# Configurar
heroku config:set REDIS_URL=$(heroku config:get REDIS_URL)
```

### Configurar domínio customizado

```bash
# Adicionar domínio
heroku domains:add seu-dominio.com

# Configurar DNS (no seu provedor)
# CNAME: seu-dominio.com -> seu-app.herokuapp.com
```

## 🔧 Modificações no Código

### src/main.py

```python
import os
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Configurar para Heroku
socketio = SocketIO(app, cors_allowed_origins="*")

# ... resto do código ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

### Remover dependências problemáticas

No Heroku, algumas dependências podem não funcionar. Remova ou substitua:

```python
# Remover ou comentar
# import psutil
# import fcntl
# import pty
```

## 📊 Monitoramento

### Ver logs

```bash
# Logs em tempo real
heroku logs --tail

# Logs específicos
heroku logs --source app

# Logs de erro
heroku logs --level error
```

### Métricas

```bash
# Ver métricas
heroku ps

# Ver uso de recursos
heroku ps:scale
```

## 🔄 Atualizações

### Deploy de atualizações

```bash
# Fazer mudanças no código
git add .
git commit -m "Atualização do painel"

# Deploy
git push heroku main

# Ver logs
heroku logs --tail
```

### Rollback

```bash
# Ver releases
heroku releases

# Fazer rollback
heroku rollback v123
```

## 💰 Limitações do Plano Gratuito

- **Dyno Hours**: 550h/mês (suficiente para 1 app 24/7)
- **Sleep**: App "dorme" após 30min de inatividade
- **Banco**: PostgreSQL limitado a 10k linhas
- **Memória**: 512MB RAM
- **Sem domínio customizado com SSL**

### Evitar o sleep

Use um serviço como [Kaffeine](https://kaffeine.herokuapp.com/) ou configure um ping:

```bash
# Adicionar ao crontab (em outro servidor)
*/25 * * * * curl https://seu-app.herokuapp.com/
```

## 🔒 Segurança

### Variáveis de ambiente

```bash
# Configurar todas as variáveis necessárias
heroku config:set SECRET_KEY="$(openssl rand -hex 32)"
heroku config:set FLASK_ENV="production"
heroku config:set DEBUG="False"
```

### SSL automático

O Heroku fornece SSL automático para apps:
- `https://seu-app.herokuapp.com`

## 🛠️ Solução de Problemas

### App não inicia

```bash
# Ver logs detalhados
heroku logs --tail

# Verificar buildpacks
heroku buildpacks

# Verificar variáveis
heroku config
```

### Erro de dependências

```bash
# Limpar cache
heroku repo:purge_cache -a seu-app

# Rebuild
git commit --allow-empty -m "Rebuild"
git push heroku main
```

### Banco de dados

```bash
# Resetar banco
heroku pg:reset DATABASE_URL

# Executar migrações
heroku run python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

## 📱 Alternativas Gratuitas

Se o Heroku não atender suas necessidades:

1. **Railway**: Similar ao Heroku, mais generoso
2. **Render**: 750h gratuitas/mês
3. **Fly.io**: Plano gratuito com limitações
4. **PythonAnywhere**: Específico para Python
5. **Vercel**: Para frontend + serverless

## 🔗 Links Úteis

- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- [Heroku Postgres](https://devcenter.heroku.com/articles/heroku-postgresql)
- [Heroku Redis](https://devcenter.heroku.com/articles/heroku-redis)

---

**✅ Deploy concluído! Seu Nazuna Panel está rodando no Heroku.**

URL do app: `https://seu-app.herokuapp.com`

