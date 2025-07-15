#!/bin/bash

# Nazuna Bot Panel - Script de Instalação Automática
# Compatível com Ubuntu 18.04+, Debian 9+, CentOS 7+

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[AVISO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Detectar sistema operacional
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        error "Sistema operacional não suportado"
    fi
    
    log "Sistema detectado: $OS $VER"
}

# Verificar se é root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Este script deve ser executado como root (use sudo)"
    fi
}

# Atualizar sistema
update_system() {
    log "Atualizando sistema..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt update && apt upgrade -y
        apt install -y curl wget git unzip software-properties-common
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum update -y
        yum install -y curl wget git unzip epel-release
    else
        warning "Sistema não testado, continuando..."
    fi
}

# Instalar Node.js
install_nodejs() {
    log "Instalando Node.js..."
    
    # Instalar Node.js 18.x
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt install -y nodejs
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum install -y nodejs npm
    fi
    
    # Verificar instalação
    node_version=$(node --version)
    npm_version=$(npm --version)
    log "Node.js instalado: $node_version"
    log "NPM instalado: $npm_version"
}

# Instalar Python e pip
install_python() {
    log "Instalando Python..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt install -y python3 python3-pip python3-venv
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum install -y python3 python3-pip
    fi
    
    python_version=$(python3 --version)
    log "Python instalado: $python_version"
}

# Instalar PM2 para gerenciamento de processos
install_pm2() {
    log "Instalando PM2..."
    npm install -g pm2
    pm2 startup
    log "PM2 instalado com sucesso"
}

# Configurar firewall
setup_firewall() {
    log "Configurando firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw --force enable
        ufw allow ssh
        ufw allow 80
        ufw allow 443
        ufw allow 5000
        log "UFW configurado"
    elif command -v firewall-cmd &> /dev/null; then
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-port=5000/tcp
        firewall-cmd --reload
        log "Firewalld configurado"
    else
        warning "Nenhum firewall detectado"
    fi
}

# Criar usuário para o painel
create_user() {
    log "Criando usuário nazuna..."
    
    if ! id "nazuna" &>/dev/null; then
        useradd -m -s /bin/bash nazuna
        usermod -aG sudo nazuna
        log "Usuário nazuna criado"
    else
        log "Usuário nazuna já existe"
    fi
}

# Baixar e configurar o painel
setup_panel() {
    log "Configurando Nazuna Panel..."
    
    # Criar diretório
    mkdir -p /opt/nazuna-panel
    cd /opt/nazuna-panel
    
    # Se o código já estiver no diretório atual, copiar
    if [[ -f "$(dirname "$0")/src/main.py" ]]; then
        cp -r "$(dirname "$0")"/* .
        log "Código copiado do diretório local"
    else
        # Caso contrário, seria necessário baixar do repositório
        warning "Código não encontrado localmente"
    fi
    
    # Configurar permissões
    chown -R nazuna:nazuna /opt/nazuna-panel
    chmod +x /opt/nazuna-panel/install.sh
    
    # Instalar dependências Python
    log "Instalando dependências Python..."
    sudo -u nazuna python3 -m venv venv
    sudo -u nazuna ./venv/bin/pip install -r requirements.txt
    
    log "Painel configurado em /opt/nazuna-panel"
}

# Configurar Nginx (opcional)
setup_nginx() {
    read -p "Deseja instalar e configurar Nginx? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Instalando Nginx..."
        
        if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
            apt install -y nginx
        elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
            yum install -y nginx
        fi
        
        # Configurar Nginx
        cat > /etc/nginx/sites-available/nazuna-panel << 'EOF'
server {
    listen 80;
    server_name _;
    
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
EOF
        
        # Ativar site
        ln -sf /etc/nginx/sites-available/nazuna-panel /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
        
        # Testar e reiniciar Nginx
        nginx -t && systemctl restart nginx
        systemctl enable nginx
        
        log "Nginx configurado"
    fi
}

# Configurar SSL com Let's Encrypt (opcional)
setup_ssl() {
    read -p "Deseja configurar SSL com Let's Encrypt? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Digite seu domínio (ex: painel.seudominio.com): " domain
        
        if [[ -n "$domain" ]]; then
            log "Instalando Certbot..."
            
            if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
                apt install -y certbot python3-certbot-nginx
            elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
                yum install -y certbot python3-certbot-nginx
            fi
            
            # Obter certificado
            certbot --nginx -d "$domain" --non-interactive --agree-tos --email admin@"$domain"
            
            # Configurar renovação automática
            (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
            
            log "SSL configurado para $domain"
        fi
    fi
}

# Criar serviços systemd
create_services() {
    log "Criando serviços systemd..."
    
    # Serviço para o painel
    cat > /etc/systemd/system/nazuna-panel.service << EOF
[Unit]
Description=Nazuna Bot Panel
After=network.target

[Service]
Type=simple
User=nazuna
WorkingDirectory=/opt/nazuna-panel
Environment=PATH=/opt/nazuna-panel/venv/bin
ExecStart=/opt/nazuna-panel/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Recarregar systemd e ativar serviços
    systemctl daemon-reload
    systemctl enable nazuna-panel
    
    log "Serviços criados"
}

# Configurar backup automático
setup_backup() {
    log "Configurando backup automático..."
    
    mkdir -p /opt/nazuna-panel/backups
    
    cat > /opt/nazuna-panel/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/nazuna-panel/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="nazuna_backup_$DATE.tar.gz"

# Criar backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude="$BACKUP_DIR" \
    --exclude="venv" \
    --exclude="node_modules" \
    --exclude="*.log" \
    /opt/nazuna-panel

# Manter apenas os últimos 7 backups
find "$BACKUP_DIR" -name "nazuna_backup_*.tar.gz" -type f -mtime +7 -delete

echo "Backup criado: $BACKUP_FILE"
EOF
    
    chmod +x /opt/nazuna-panel/backup.sh
    chown nazuna:nazuna /opt/nazuna-panel/backup.sh
    
    # Adicionar ao crontab
    (sudo -u nazuna crontab -l 2>/dev/null; echo "0 2 * * * /opt/nazuna-panel/backup.sh") | sudo -u nazuna crontab -
    
    log "Backup automático configurado (diário às 2h)"
}

# Função principal
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    NAZUNA BOT PANEL                          ║"
    echo "║                  Instalação Automática                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "Iniciando instalação..."
    
    check_root
    detect_os
    update_system
    install_nodejs
    install_python
    install_pm2
    setup_firewall
    create_user
    setup_panel
    setup_nginx
    setup_ssl
    create_services
    setup_backup
    
    # Iniciar serviços
    log "Iniciando serviços..."
    systemctl start nazuna-panel
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   INSTALAÇÃO CONCLUÍDA!                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    info "Painel instalado em: /opt/nazuna-panel"
    info "Acesse o painel em: http://$(curl -s ifconfig.me):5000"
    info "Logs do serviço: journalctl -u nazuna-panel -f"
    info "Gerenciar serviço: systemctl {start|stop|restart|status} nazuna-panel"
    
    echo
    log "Comandos úteis:"
    echo "  - Ver status: systemctl status nazuna-panel"
    echo "  - Ver logs: journalctl -u nazuna-panel -f"
    echo "  - Reiniciar: systemctl restart nazuna-panel"
    echo "  - Backup manual: /opt/nazuna-panel/backup.sh"
    
    echo
    warning "Lembre-se de:"
    echo "  1. Configurar o bot Nazuna em /opt/nazuna-panel/nazuna/"
    echo "  2. Ajustar as configurações em /opt/nazuna-panel/src/config.py"
    echo "  3. Verificar o firewall e portas abertas"
    
    log "Instalação finalizada com sucesso!"
}

# Executar instalação
main "$@"

