#!/bin/bash

# Nazuna Bot Panel - Script de Instalação Automática para Termux

set -e

# Cores para output
RED=\'\\033[0;31m\'
GREEN=\'\\033[0;32m\'
YELLOW=\'\\033[1;33m\'
BLUE=\'\\033[0;34m\'
NC=\'\\033[0m\' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +\'%Y-%m-%d %H:%M:%S\')] $1${NC}"
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

# Verificar se está no Termux
check_termux() {
    if [[ -z "$PREFIX" ]]; then
        error "Este script deve ser executado no Termux."
    fi
}

# Atualizar sistema e instalar dependências
install_dependencies() {
    log "Atualizando sistema e instalando dependências..."
    pkg update && pkg upgrade -y
    pkg install -y git python nodejs-lts
    npm install -g pnpm
}

# Clonar o repositório
clone_repo() {
    log "Clonando repositório do Nazuna Panel..."
    
    if [ -d "nazuna-panel-backend" ]; then
        warning "Diretório nazuna-panel-backend já existe. Pulando clonagem."
        cd nazuna-panel-backend
    else
        git clone https://github.com/Pauloh2206/Panel-BOT.git
        cd Panel-BOT
    fi
}

# Configurar e instalar backend
setup_backend() {
    log "Configurando backend Flask..."
    cd nazuna-panel-backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    log "Instalando dependências Node.js para o bot Nazuna..."
    cd nazuna
    npm install
    cd ..
    
    log "Backend configurado."
}

# Configurar e instalar frontend
setup_frontend() {
    log "Configurando frontend React..."
    cd ../nazuna-panel-frontend
    pnpm install
    pnpm run build
    
    # Copiar build para o static do backend
    rm -rf ../nazuna-panel-backend/static/*
    cp -r dist/* ../nazuna-panel-backend/static/
    
    log "Frontend configurado."
}

# Função principal
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    NAZUNA BOT PANEL                          ║"
    echo "║                  Instalação Automática (Termux)             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "Iniciando instalação..."
    
    check_termux
    install_dependencies
    clone_repo
    setup_backend
    setup_frontend
    
    log "Instalação concluída!"
    info "Para iniciar o backend: cd nazuna-panel-backend && source venv/bin/activate && nohup python src/main.py > backend.log 2>&1 &"
    info "Para iniciar o frontend: cd nazuna-panel-frontend && pnpm run dev --host"
    info "Acesse o painel em: http://localhost:5173"
    warning "Lembre-se de configurar o bot Nazuna e suas configurações no painel."
}

# Executar instalação
main "$@"

