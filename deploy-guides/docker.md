# 🐳 Guia de Deploy - Docker

Deploy do Nazuna Panel usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🚀 Deploy Rápido

### Passo 1: Clonar repositório

```bash
git clone https://github.com/seu-usuario/nazuna-panel.git
cd nazuna-panel
```

### Passo 2: Configurar variáveis

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar variáveis
nano .env
```

### Passo 3: Iniciar com Docker Compose

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

## 📁 Estrutura Docker

### docker-compose.yml

```yaml
version: '3.8'

services:
  nazuna-panel:
    build: .
    container_name: nazuna-panel
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./nazuna:/app/nazuna
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
      - ./config:/app/config
    environment:
      - NODE_ENV=production
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://nazuna:password@postgres:5432/nazuna
      - REDIS_URL=redis://redis:6379/0
    networks:
      - nazuna-network
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    container_name: nazuna-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=nazuna
      - POSTGRES_USER=nazuna
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups/postgres:/backups
    networks:
      - nazuna-network

  redis:
    image: redis:7-alpine
    container_name: nazuna-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - nazuna-network

  nginx:
    image: nginx:alpine
    container_name: nazuna-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites:/etc/nginx/conf.d
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - nazuna-panel
    networks:
      - nazuna-network

volumes:
  postgres_data:
  redis_data:

networks:
  nazuna-network:
    driver: bridge
```

### Dockerfile

```dockerfile
# Multi-stage build
FROM node:18-bullseye as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# Main image
FROM python:3.11-slim-bullseye

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 nazuna

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Copiar frontend buildado
COPY --from=frontend-builder /app/frontend/dist ./static

# Criar diretórios necessários
RUN mkdir -p data logs backups nazuna config

# Configurar permissões
RUN chown -R nazuna:nazuna /app
RUN chmod +x start.sh

# Mudar para usuário não-root
USER nazuna

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização
CMD ["./start.sh"]
```

### .env.example

```bash
# Aplicação
SECRET_KEY=sua-chave-secreta-super-segura
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Banco de dados
DATABASE_URL=postgresql://nazuna:password@postgres:5432/nazuna
POSTGRES_DB=nazuna
POSTGRES_USER=nazuna
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379/0

# Bot Nazuna
NAZUNA_PATH=/app/nazuna
BOT_PREFIX=!
BOT_NAME=Nazuna
OWNER_NAME=Admin
OWNER_NUMBER=5511999999999

# Logs
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=7
```

## 🔧 Configuração Nginx

### nginx/nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logs
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Include sites
    include /etc/nginx/conf.d/*.conf;
}
```

### nginx/sites/nazuna-panel.conf

```nginx
upstream nazuna_backend {
    server nazuna-panel:5000;
}

server {
    listen 80;
    server_name _;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Proxy to backend
    location / {
        proxy_pass http://nazuna_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://nazuna_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔒 SSL/TLS

### Gerar certificados auto-assinados

```bash
# Criar diretório SSL
mkdir -p ssl

# Gerar certificado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=BR/ST=SP/L=SP/O=Nazuna/CN=localhost"
```

### Let's Encrypt com Certbot

```bash
# Adicionar serviço certbot ao docker-compose.yml
certbot:
  image: certbot/certbot
  container_name: nazuna-certbot
  volumes:
    - ./ssl:/etc/letsencrypt
    - ./nginx/html:/var/www/html
  command: certonly --webroot --webroot-path=/var/www/html --email seu@email.com --agree-tos --no-eff-email -d seu-dominio.com
```

## 📊 Monitoramento

### Adicionar Prometheus + Grafana

```yaml
# Adicionar ao docker-compose.yml
prometheus:
  image: prom/prometheus
  container_name: nazuna-prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  networks:
    - nazuna-network

grafana:
  image: grafana/grafana
  container_name: nazuna-grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
  networks:
    - nazuna-network
```

### monitoring/prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'nazuna-panel'
    static_configs:
      - targets: ['nazuna-panel:5000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

## 🔄 Backup Automático

### Script de backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U nazuna nazuna > "$BACKUP_DIR/postgres_$DATE.sql"

# Backup arquivos
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" \
    --exclude="$BACKUP_DIR" \
    --exclude="logs" \
    /app

# Limpar backups antigos (manter 7 dias)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

### Cron para backup

```yaml
# Adicionar ao docker-compose.yml
backup:
  image: alpine:latest
  container_name: nazuna-backup
  volumes:
    - ./backups:/backups
    - ./backup.sh:/backup.sh
  command: crond -f
  environment:
    - CRONTAB=0 2 * * * /backup.sh
```

## 🛠️ Comandos Úteis

### Gerenciamento básico

```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Reiniciar serviço específico
docker-compose restart nazuna-panel

# Ver logs
docker-compose logs -f nazuna-panel

# Executar comando no container
docker-compose exec nazuna-panel bash

# Atualizar imagens
docker-compose pull
docker-compose up -d
```

### Manutenção do banco

```bash
# Backup do banco
docker-compose exec postgres pg_dump -U nazuna nazuna > backup.sql

# Restaurar banco
docker-compose exec -T postgres psql -U nazuna nazuna < backup.sql

# Conectar ao banco
docker-compose exec postgres psql -U nazuna nazuna
```

### Logs e debug

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f nazuna-panel
docker-compose logs -f postgres
docker-compose logs -f nginx

# Ver uso de recursos
docker stats

# Inspecionar container
docker inspect nazuna-panel
```

## 🔧 Solução de Problemas

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs nazuna-panel

# Verificar configuração
docker-compose config

# Rebuild da imagem
docker-compose build --no-cache nazuna-panel
```

### Problemas de rede

```bash
# Verificar rede
docker network ls
docker network inspect nazuna-panel_nazuna-network

# Testar conectividade
docker-compose exec nazuna-panel ping postgres
docker-compose exec nazuna-panel ping redis
```

### Problemas de permissão

```bash
# Corrigir permissões
sudo chown -R 1000:1000 data logs backups

# Verificar usuário no container
docker-compose exec nazuna-panel id
```

## 🚀 Deploy em Produção

### Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml nazuna

# Ver serviços
docker service ls

# Escalar serviço
docker service scale nazuna_nazuna-panel=3
```

### Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nazuna-panel
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nazuna-panel
  template:
    metadata:
      labels:
        app: nazuna-panel
    spec:
      containers:
      - name: nazuna-panel
        image: nazuna-panel:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: nazuna-secrets
              key: database-url
```

## 📱 Integração CI/CD

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Docker Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t nazuna-panel .
    
    - name: Deploy to production
      run: |
        docker-compose down
        docker-compose pull
        docker-compose up -d
```

---

**✅ Deploy Docker concluído! Seu Nazuna Panel está rodando em containers.**

- 🌐 **URL**: `http://localhost` ou `https://localhost`
- 📊 **Grafana**: `http://localhost:3000` (admin/admin)
- 🔍 **Prometheus**: `http://localhost:9090`

