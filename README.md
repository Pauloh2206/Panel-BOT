# 🤖 NAZUNA BOT PANEL - ENTREGA FINAL

## 📋 Resumo do Projeto

Painel de gerenciamento web completo para o bot Nazuna, desenvolvido com tecnologias modernas e design profissional. O sistema permite controle total do bot WhatsApp através de uma interface web intuitiva.

## ✨ Funcionalidades Implementadas

### 🎛️ **Painel de Controle**
- ✅ Dashboard com métricas em tempo real
- ✅ Controle do bot (iniciar, parar, reiniciar)
- ✅ Monitoramento de status e performance
- ✅ Configurações avançadas do bot

### 💻 **Terminal Integrado**
- ✅ Terminal web interativo
- ✅ Execução de comandos em tempo real
- ✅ Histórico de comandos
- ✅ Interface similar ao terminal nativo

### 📁 **Gerenciador de Arquivos**
- ✅ Upload e download de arquivos
- ✅ Editor de código integrado
- ✅ Navegação por diretórios
- ✅ Gerenciamento de arquivos do bot

### ⚙️ **Configurações**
- ✅ Interface para configurar o bot
- ✅ Modos de operação (Normal, Dual, Code)
- ✅ Configurações de prefixo, nome, etc.
- ✅ Salvamento automático

### 🎨 **Design Moderno**
- ✅ Interface dark theme profissional
- ✅ Responsivo para mobile e desktop
- ✅ Animações e transições suaves
- ✅ Componentes UI modernos

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Flask** - Framework web Python
- **Flask-SocketIO** - WebSocket para tempo real
- **Flask-CORS** - Suporte a CORS
- **SQLite** - Banco de dados
- **Python 3.11** - Linguagem principal

### **Frontend**
- **React 18** - Framework frontend
- **Vite** - Build tool moderna
- **Tailwind CSS** - Framework CSS
- **Lucide React** - Ícones modernos
- **Socket.IO Client** - WebSocket cliente
- **Sonner** - Notificações toast

### **Infraestrutura**
- **Docker** - Containerização
- **Nginx** - Proxy reverso
- **PM2** - Gerenciador de processos
- **Systemd** - Serviços do sistema

## 📦 Estrutura do Projeto

```
nazuna-panel/
├── nazuna-panel-backend/          # Backend Flask
│   ├── src/
│   │   ├── main.py               # Aplicação principal
│   │   ├── routes/               # Rotas da API
│   │   │   ├── bot.py           # Controle do bot
│   │   │   ├── terminal.py      # Terminal
│   │   │   ├── files.py         # Arquivos
│   │   │   └── socket_events.py # WebSocket
│   │   └── models/              # Modelos do banco
│   ├── static/                  # Frontend compilado
│   ├── requirements.txt         # Dependências Python
│   ├── install.sh              # Script de instalação para VPS
│   ├── install-termux.sh       # Script de instalação para Termux
│   ├── start.sh                # Script de inicialização
│   ├── Dockerfile              # Docker
│   ├── docker-compose.yml      # Docker Compose
│   └── deploy-guides/          # Guias de deploy
│       ├── vps-ubuntu.md       # VPS Ubuntu
│       ├── heroku.md           # Heroku
│       ├── railway.md          # Railway
│       └── docker.md           # Docker
├── nazuna-panel-frontend/        # Frontend React
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   │   ├── Dashboard.jsx    # Dashboard
│   │   │   ├── BotController.jsx # Controle do bot
│   │   │   ├── Terminal.jsx     # Terminal
│   │   │   ├── FileManager.jsx  # Arquivos
│   │   │   └── Settings.jsx     # Configurações
│   │   ├── App.jsx             # App principal
│   │   └── App.css             # Estilos
│   ├── package.json            # Dependências Node
│   └── vite.config.js          # Configuração Vite
└── nazuna/                     # Bot Nazuna (clonado)
```

## 🚀 Opções de Instalação Automatizada

Oferecemos scripts de instalação automatizada para simplificar o deploy em diferentes ambientes. Escolha a opção que melhor se adapta às suas necessidades:

### 1. **Instalação em VPS/Servidor (Linux)**

Este script automatiza a instalação completa em servidores Linux (Ubuntu, Debian, CentOS, RHEL).

```bash
# Baixar o script de instalação
wget https://raw.githubusercontent.com/Pauloh2206/Panel-BOT/main/nazuna-panel-backend/install.sh

# Tornar o script executável
chmod +x install.sh

# Executar o script (como root ou com sudo)
sudo ./install.sh

# Opções adicionais (ex: com Nginx e SSL)
# sudo ./install.sh --nginx --ssl --domain seu.dominio.com
```

**Características:**
- ✅ Instalação completa de dependências (Python, Node.js, pnpm)
- ✅ Configuração de ambiente virtual Python
- ✅ Instalação do bot Nazuna e suas dependências
- ✅ Configuração de usuário dedicado (`nazuna`)
- ✅ Configuração de firewall (UFW/Firewalld)
- ✅ Criação de serviço `systemd` para o painel
- ✅ Configuração opcional de Nginx como proxy reverso
- ✅ Configuração opcional de SSL com Let's Encrypt
- ✅ Configuração de backup automático

### 2. **Instalação no Termux (Android)**

Este script é otimizado para a instalação em dispositivos Android via Termux.

```bash
# Baixar o script de instalação
wget https://raw.githubusercontent.com/Pauloh2206/Panel-BOT/main/nazuna-panel-backend/install-termux.sh

# Tornar o script executável
chmod +x install-termux.sh

# Executar o script
./install-termux.sh
```

**Características:**
- ✅ Instalação de dependências (Python, Node.js, pnpm) via `pkg`
- ✅ Clonagem do repositório
- ✅ Configuração do backend Flask
- ✅ Instalação do bot Nazuna e suas dependências
- ✅ Build e cópia do frontend para o backend
- ✅ Instruções claras para iniciar o backend e frontend

### 3. **Docker (Recomendado para Desenvolvedores e Produção)**

Utilize Docker para uma instalação isolada e portátil.

```bash
# Clonar o repositório
git clone https://github.com/Pauloh2206/Panel-BOT.git
cd Panel-BOT

# Iniciar com Docker Compose
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

**Características:**
- ✅ Isolamento completo do ambiente
- ✅ Fácil portabilidade entre sistemas
- ✅ Gerenciamento simplificado de dependências
- ✅ Escalabilidade e orquestração com Docker Compose

### 4. **Heroku (Hospedagem Gratuita)**

Para deploy rápido e gratuito (com limitações de plano).

```bash
# Certifique-se de ter o Heroku CLI instalado e logado
heroku create seu-app-nazuna # Crie um novo app Heroku
git push heroku main         # Faça o deploy do seu código
heroku open                  # Abra o app no navegador
```

**Características:**
- ✅ Deploy gratuito
- ✅ SSL automático
- ✅ Escalabilidade automática
- ✅ Integração com GitHub
- ⚠️ Limitações do plano gratuito

### 5. **Railway (Moderno e Fácil)**

Plataforma moderna com deploy automático via GitHub.

```bash
# Conecte seu repositório GitHub (Pauloh2206/Panel-BOT) no painel do Railway.
# O deploy será automático a cada push para a branch principal.
```

**Características:**
- ✅ Deploy automático
- ✅ $5 gratuitos/mês
- ✅ SSL automático
- ✅ Domínio customizado
- ✅ Métricas avançadas

## 🔧 Configuração Pós-Instalação

### 1. **Configurar o Bot Nazuna**

```bash
# Se o bot não foi clonado automaticamente pelo script de instalação, faça-o:
cd /opt/nazuna-panel # Ou o diretório onde o painel foi instalado
git clone https://github.com/hiudyy/nazuna.git nazuna

# Instalar dependências do bot
cd nazuna
npm install

# Configurar o bot conforme documentação original do Nazuna
```

### 2. **Acessar o Painel**

- **Local (desenvolvimento)**: `http://localhost:5173` (após iniciar frontend e backend)
- **VPS (padrão)**: `http://SEU_IP:5000`
- **VPS (com Nginx)**: `http://SEU_DOMINIO`
- **VPS (com Nginx e SSL)**: `https://SEU_DOMINIO`

### 3. **Configurações Iniciais**

1. Acesse "Configurações" no painel
2. Configure:
   - Prefixo dos comandos (ex: `!`)
   - Nome do bot (ex: `Nazuna`)
   - Número do dono
   - Mensagem de boas-vindas
3. Salve as configurações
4. Inicie o bot pelo painel

## 📊 Monitoramento e Logs

### **Logs do Sistema**
```bash
# Ver logs do painel (para instalações via install.sh)
sudo journalctl -u nazuna-panel -f

# Ver logs do Nginx (se configurado)
sudo tail -f /var/log/nginx/access.log

# Ver logs da aplicação (se configurado)
sudo tail -f /opt/nazuna-panel/logs/app.log
```

### **Comandos Úteis**
```bash
# Status do serviço (para instalações via install.sh)
sudo systemctl status nazuna-panel

# Reiniciar serviço (para instalações via install.sh)
sudo systemctl restart nazuna-panel

# Backup manual
sudo /opt/nazuna-panel/backup.sh

# Atualizar painel (para instalações via install.sh)
cd /opt/nazuna-panel
sudo -u nazuna git pull
sudo systemctl restart nazuna-panel
```

## 🔒 Segurança

### **Configurações Implementadas**
- ✅ Firewall configurado (UFW/Firewalld)
- ✅ SSL/TLS com Let's Encrypt
- ✅ Usuário dedicado (nazuna)
- ✅ Permissões restritivas
- ✅ Headers de segurança no Nginx
- ✅ Variáveis de ambiente para senhas

### **Recomendações Adicionais**
- 🔐 Use senhas fortes
- 🔑 Configure chaves SSH
- 🛡️ Mantenha o sistema atualizado
- 📊 Monitore logs regularmente
- 💾 Faça backups regulares

## 📱 Compatibilidade

### **Navegadores Suportados**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers

### **Sistemas Operacionais**
- ✅ Ubuntu 18.04+
- ✅ Debian 9+
- ✅ CentOS 7+
- ✅ RHEL 7+
- ✅ Docker (qualquer SO)
- ✅ Termux (Android)

### **Requisitos Mínimos**
- 💾 **RAM**: 1GB (recomendado 2GB)
- 💿 **Disco**: 10GB livres
- 🌐 **Rede**: Conexão estável
- 🐍 **Python**: 3.8+
- 📦 **Node.js**: 16+

## 🆘 Suporte e Solução de Problemas

### **Problemas Comuns**

1. **Painel não carrega**
   ```bash
   sudo systemctl status nazuna-panel
   sudo journalctl -u nazuna-panel -f
   ```

2. **Bot não inicia**
   - Verificar se o Node.js está instalado
   - Verificar dependências do bot Nazuna
   - Verificar configurações no painel

3. **Erro de permissões**
   ```bash
   sudo chown -R nazuna:nazuna /opt/nazuna-panel
   ```

4. **Porta em uso**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 PID
   ```

### **Logs de Debug**
```bash
# Ativar modo debug
export FLASK_DEBUG=True
python src/main.py

# Ver logs detalhados
sudo journalctl -u nazuna-panel -f --no-pager
```

## 📞 Contato e Documentação

### **Documentação Completa**
- 📖 **README.md** - Documentação principal
- 🐧 **vps-ubuntu.md** - Guia VPS Ubuntu
- ☁️ **heroku.md** - Deploy Heroku
- 🚂 **railway.md** - Deploy Railway
- 🐳 **docker.md** - Deploy Docker

### **Arquivos Importantes**
- 🔧 **install.sh** - Script de instalação automática para VPS
- 📱 **install-termux.sh** - Script de instalação automática para Termux
- 🚀 **start.sh** - Script de inicialização
- 🐳 **docker-compose.yml** - Configuração Docker
- ⚙️ **requirements.txt** - Dependências Python

## ✅ Status da Entrega

### **Funcionalidades Principais**
- ✅ Painel de controle completo
- ✅ Interface moderna e responsiva
- ✅ Terminal integrado funcional
- ✅ Gerenciador de arquivos
- ✅ Sistema de configurações
- ✅ WebSocket para tempo real
- ✅ Dashboard com métricas

### **Instalação e Deploy**
- ✅ Script de instalação automática para VPS
- ✅ Script de instalação automática para Termux
- ✅ Suporte a múltiplas plataformas
- ✅ Docker e Docker Compose
- ✅ Guias detalhados de deploy
- ✅ Configuração de SSL/Nginx
- ✅ Backup automático

### **Documentação**
- ✅ README completo e atualizado
- ✅ Guias específicos por plataforma
- ✅ Solução de problemas
- ✅ Comandos úteis
- ✅ Configurações de segurança

---

## 🎉 **PROJETO CONCLUÍDO COM SUCESSO!**

O Nazuna Bot Panel está pronto para uso em produção com:
- 🎨 **Interface profissional e moderna**
- 🛠️ **Instalação simples em qualquer ambiente**
- 📱 **Compatibilidade total com mobile**
- 🔒 **Segurança implementada**
- 📚 **Documentação completa**

**Acesse o painel e comece a gerenciar seu bot Nazuna de forma profissional!**



