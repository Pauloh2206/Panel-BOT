# 🤖 Nazuna Bot Panel

Painel de gerenciamento web moderno e intuitivo para o bot Nazuna, com interface responsiva e funcionalidades avançadas.

## ✨ Características

- 🎨 **Interface Moderna**: Design responsivo e intuitivo
- 🔧 **Controle Completo**: Iniciar, parar e reiniciar o bot
- 💻 **Terminal Integrado**: Execute comandos diretamente no painel
- 📁 **Gerenciador de Arquivos**: Edite e gerencie arquivos do bot
- ⚙️ **Configurações**: Interface para ajustar configurações do bot
- 📊 **Dashboard**: Monitoramento em tempo real do sistema
- 🔄 **Atualizações em Tempo Real**: WebSocket para updates instantâneos

## 🚀 Instalação Rápida

### Método 1: Script Automático (Recomendado)

```bash
# Baixar e executar o instalador
curl -fsSL https://raw.githubusercontent.com/seu-usuario/nazuna-panel/main/install.sh | sudo bash
```

### Método 2: Instalação Manual

#### Pré-requisitos
- Ubuntu 18.04+ / Debian 9+ / CentOS 7+
- Python 3.8+
- Node.js 16+
- Git

#### Passo a passo

1. **Clonar o repositório**
```bash
git clone https://github.com/seu-usuario/nazuna-panel.git
cd nazuna-panel
```

2. **Executar instalação**
```bash
sudo chmod +x install.sh
sudo ./install.sh
```

3. **Iniciar o painel**
```bash
sudo systemctl start nazuna-panel
sudo systemctl enable nazuna-panel
```

### Método 3: Docker (Para desenvolvedores)

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/nazuna-panel.git
cd nazuna-panel

# Iniciar com Docker Compose
docker-compose up -d

# Verificar logs
docker-compose logs -f nazuna-panel
```

## 📋 Configuração

### Configuração Básica

1. **Acesse o painel**: `http://seu-ip:5000`
2. **Configure o bot**: Vá em "Configurações" e ajuste:
   - Prefixo dos comandos
   - Nome do bot
   - Número do dono
   - Outras configurações específicas

### Configuração Avançada

Edite o arquivo `/opt/nazuna-panel/src/config.py`:

```python
class Config:
    SECRET_KEY = 'sua-chave-secreta'
    DATABASE_URL = 'sqlite:///data/nazuna.db'
    NAZUNA_PATH = './nazuna'
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 5000
```

### Variáveis de Ambiente

```bash
export SECRET_KEY="sua-chave-secreta"
export DATABASE_URL="sqlite:///data/nazuna.db"
export NAZUNA_PATH="./nazuna"
export FLASK_DEBUG="False"
export HOST="0.0.0.0"
export PORT="5000"
```

## 🔧 Gerenciamento

### Comandos do Sistema

```bash
# Ver status
sudo systemctl status nazuna-panel

# Iniciar
sudo systemctl start nazuna-panel

# Parar
sudo systemctl stop nazuna-panel

# Reiniciar
sudo systemctl restart nazuna-panel

# Ver logs
sudo journalctl -u nazuna-panel -f

# Ver logs específicos
sudo tail -f /opt/nazuna-panel/logs/app.log
```

### Backup e Restauração

```bash
# Backup manual
sudo /opt/nazuna-panel/backup.sh

# Restaurar backup
sudo tar -xzf /opt/nazuna-panel/backups/nazuna_backup_YYYYMMDD_HHMMSS.tar.gz -C /

# Backups automáticos são criados diariamente às 2h
```

## 🌐 Configuração com Nginx

### SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Configuração Manual do Nginx

```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🐳 Docker

### Docker Compose

```yaml
version: '3.8'
services:
  nazuna-panel:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./nazuna:/app/nazuna
      - ./data:/app/data
    environment:
      - NODE_ENV=production
      - FLASK_ENV=production
```

### Comandos Docker

```bash
# Construir imagem
docker build -t nazuna-panel .

# Executar container
docker run -d -p 5000:5000 --name nazuna-panel nazuna-panel

# Ver logs
docker logs -f nazuna-panel

# Acessar container
docker exec -it nazuna-panel bash
```

## 📱 Hospedagem

### VPS Recomendadas

- **DigitalOcean**: Droplet básico (1GB RAM)
- **Vultr**: VPS básico (1GB RAM)
- **Linode**: Nanode (1GB RAM)
- **AWS**: EC2 t2.micro (Free tier)
- **Google Cloud**: e2-micro (Free tier)

### Hospedagem Compartilhada

Para hospedagem compartilhada com suporte a Python:

1. **PythonAnywhere**
2. **Heroku**
3. **Railway**
4. **Render**

### Configuração para Heroku

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Criar app
heroku create seu-app-nazuna

# Deploy
git push heroku main

# Ver logs
heroku logs --tail
```

## 🔒 Segurança

### Configurações Recomendadas

1. **Firewall**
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

2. **Usuário dedicado**
```bash
sudo useradd -m -s /bin/bash nazuna
sudo usermod -aG sudo nazuna
```

3. **Chaves SSH**
```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id nazuna@seu-servidor
```

4. **Fail2Ban**
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
nazuna-panel/
├── src/
│   ├── main.py              # Aplicação principal
│   ├── routes/              # Rotas da API
│   │   ├── bot.py          # Controle do bot
│   │   ├── terminal.py     # Terminal
│   │   ├── files.py        # Gerenciador de arquivos
│   │   └── socket_events.py # WebSocket
│   └── models/             # Modelos do banco
├── static/                 # Frontend compilado
├── templates/              # Templates (se necessário)
├── requirements.txt        # Dependências Python
├── package.json           # Dependências Node.js
├── install.sh             # Script de instalação
├── start.sh               # Script de inicialização
├── docker-compose.yml     # Docker Compose
├── Dockerfile             # Docker
└── README.md              # Documentação
```

### Ambiente de Desenvolvimento

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/nazuna-panel.git
cd nazuna-panel

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar em modo desenvolvimento
export FLASK_DEBUG=True
python src/main.py
```

## 📞 Suporte

### Problemas Comuns

1. **Porta 5000 em uso**
```bash
sudo lsof -i :5000
sudo kill -9 PID
```

2. **Permissões negadas**
```bash
sudo chown -R nazuna:nazuna /opt/nazuna-panel
sudo chmod +x /opt/nazuna-panel/start.sh
```

3. **Bot não inicia**
- Verificar se o Node.js está instalado
- Verificar dependências do bot Nazuna
- Verificar logs: `journalctl -u nazuna-panel -f`

### Logs e Debug

```bash
# Logs do sistema
sudo journalctl -u nazuna-panel -f

# Logs da aplicação
sudo tail -f /opt/nazuna-panel/logs/app.log

# Debug mode
export FLASK_DEBUG=True
python src/main.py
```

### Contato

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/nazuna-panel/issues)
- **Documentação**: [Wiki](https://github.com/seu-usuario/nazuna-panel/wiki)
- **Telegram**: @seu-usuario

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## ⭐ Agradecimentos

- [Nazuna Bot](https://github.com/hiudyy/nazuna) - Bot base
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [React](https://reactjs.org/) - Frontend
- [Socket.IO](https://socket.io/) - WebSocket

---

**Feito com ❤️ para a comunidade de bots WhatsApp**

