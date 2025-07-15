# Usar imagem base com Python e Node.js
FROM node:18-bullseye

# Instalar Python e dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt package*.json ./

# Instalar dependências Python
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Instalar dependências Node.js (para o bot)
RUN npm install

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p data logs backups nazuna

# Configurar permissões
RUN chmod +x install.sh start.sh

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["./start.sh"]

