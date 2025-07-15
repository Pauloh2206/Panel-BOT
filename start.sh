#!/bin/bash

# Script de inicialização do Nazuna Panel
set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    NAZUNA BOT PANEL                          ║"
echo "║                     Iniciando...                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se está em container
if [ -f /.dockerenv ]; then
    log "Executando em container Docker"
    PYTHON_CMD="/app/venv/bin/python"
    WORK_DIR="/app"
else
    log "Executando em sistema host"
    PYTHON_CMD="./venv/bin/python"
    WORK_DIR="/opt/nazuna-panel"
fi

# Ir para diretório de trabalho
cd "$WORK_DIR" || exit 1

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    log "Criando ambiente virtual Python..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# Verificar se o bot Nazuna existe
if [ ! -d "nazuna" ]; then
    info "Bot Nazuna não encontrado. Clonando repositório..."
    git clone https://github.com/hiudyy/nazuna.git nazuna || {
        log "Erro ao clonar repositório. Criando diretório vazio..."
        mkdir -p nazuna
    }
fi

# Instalar dependências do bot se necessário
if [ -f "nazuna/package.json" ] && [ ! -d "nazuna/node_modules" ]; then
    log "Instalando dependências do bot Nazuna..."
    cd nazuna
    npm install
    cd ..
fi

# Criar diretórios necessários
mkdir -p data logs backups

# Verificar configuração
if [ ! -f "src/config.py" ]; then
    log "Criando arquivo de configuração padrão..."
    cat > src/config.py << 'EOF'
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nazuna-panel-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///data/nazuna.db'
    NAZUNA_PATH = os.environ.get('NAZUNA_PATH') or './nazuna'
    DEBUG = os.environ.get('FLASK_DEBUG') == 'True'
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
EOF
fi

# Aguardar serviços dependentes (se em Docker)
if [ -f /.dockerenv ]; then
    log "Aguardando serviços dependentes..."
    sleep 5
fi

# Inicializar banco de dados
log "Inicializando banco de dados..."
$PYTHON_CMD -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Banco de dados inicializado')
"

# Verificar saúde do sistema
log "Verificando saúde do sistema..."
$PYTHON_CMD -c "
import sys
import os
print(f'Python: {sys.version}')
print(f'Diretório: {os.getcwd()}')
print(f'Nazuna existe: {os.path.exists(\"nazuna\")}')
"

# Iniciar aplicação
log "Iniciando Nazuna Panel..."
info "Acesse o painel em: http://localhost:5000"

exec $PYTHON_CMD src/main.py

