# 🐧 Guia de Instalação - VPS Ubuntu

Este guia detalha a instalação do Nazuna Panel em um VPS Ubuntu 20.04/22.04.

## 📋 Pré-requisitos

- VPS com Ubuntu 20.04+ 
- Mínimo 1GB RAM
- 10GB de espaço em disco
- Acesso root ou sudo
- Conexão SSH

## 🚀 Instalação Automática (Recomendado)

### Passo 1: Conectar ao VPS

```bash
ssh root@SEU_IP_VPS
# ou
ssh usuario@SEU_IP_VPS
```

### Passo 2: Baixar e executar o instalador

```bash
# Baixar o instalador
wget https://raw.githubusercontent.com/seu-usuario/nazuna-panel/main/install.sh

# Dar permissão de execução
chmod +x install.sh

# Executar instalação
sudo ./install.sh
```

### Passo 3: Aguardar a instalação

O script irá:
- ✅ Atualizar o sistema
- ✅ Instalar Node.js 18.x
- ✅ Instalar Python 3.8+
- ✅ Instalar PM2
- ✅ Configurar firewall
- ✅ Criar usuário nazuna
- ✅ Instalar o painel
- ✅ Configurar Nginx (opcional)
- ✅ Configurar SSL (opcional)
- ✅ Criar serviços systemd
- ✅ Configurar backup automático

## 🔧 Instalação Manual

### Passo 1: Atualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git unzip software-properties-common
```

### Passo 2: Instalar Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Passo 3: Instalar Python

```bash
sudo apt install -y python3 python3-pip python3-venv
```

### Passo 4: Instalar PM2

```bash
sudo npm install -g pm2
pm2 startup
```

### Passo 5: Configurar firewall

```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
```

### Passo 6: Criar usuário

```bash
sudo useradd -m -s /bin/bash nazuna
sudo usermod -aG sudo nazuna
```

### Passo 7: Instalar o painel

```bash
# Baixar código
sudo mkdir -p /opt/nazuna-panel
cd /opt/nazuna-panel
sudo git clone https://github.com/seu-usuario/nazuna-panel.git .

# Configurar permissões
sudo chown -R nazuna:nazuna /opt/nazuna-panel

# Instalar dependências Python
sudo -u nazuna python3 -m venv venv
sudo -u nazuna ./venv/bin/pip install -r requirements.txt
```

### Passo 8: Configurar serviço

```bash
sudo tee /etc/systemd/system/nazuna-panel.service > /dev/null <<EOF
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

sudo systemctl daemon-reload
sudo systemctl enable nazuna-panel
sudo systemctl start nazuna-panel
```

## 🌐 Configurar Nginx (Opcional)

### Instalar Nginx

```bash
sudo apt install -y nginx
```

### Configurar site

```bash
sudo tee /etc/nginx/sites-available/nazuna-panel > /dev/null <<EOF
server {
    listen 80;
    server_name SEU_DOMINIO_OU_IP;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/nazuna-panel /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar e reiniciar
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔒 Configurar SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado (substitua SEU_DOMINIO)
sudo certbot --nginx -d SEU_DOMINIO

# Configurar renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## ✅ Verificar Instalação

### Verificar serviços

```bash
# Status do painel
sudo systemctl status nazuna-panel

# Status do Nginx
sudo systemctl status nginx

# Ver logs
sudo journalctl -u nazuna-panel -f
```

### Testar acesso

```bash
# Testar localmente
curl http://localhost:5000

# Verificar porta
sudo netstat -tlnp | grep :5000
```

### Acessar painel

- **Sem Nginx**: `http://SEU_IP:5000`
- **Com Nginx**: `http://SEU_DOMINIO` ou `http://SEU_IP`
- **Com SSL**: `https://SEU_DOMINIO`

## 🛠️ Comandos Úteis

### Gerenciar serviço

```bash
# Iniciar
sudo systemctl start nazuna-panel

# Parar
sudo systemctl stop nazuna-panel

# Reiniciar
sudo systemctl restart nazuna-panel

# Status
sudo systemctl status nazuna-panel

# Logs em tempo real
sudo journalctl -u nazuna-panel -f
```

### Atualizar painel

```bash
cd /opt/nazuna-panel
sudo -u nazuna git pull
sudo systemctl restart nazuna-panel
```

### Backup manual

```bash
sudo /opt/nazuna-panel/backup.sh
```

## 🔧 Solução de Problemas

### Painel não inicia

```bash
# Verificar logs
sudo journalctl -u nazuna-panel -f

# Verificar permissões
sudo chown -R nazuna:nazuna /opt/nazuna-panel

# Verificar dependências
cd /opt/nazuna-panel
sudo -u nazuna ./venv/bin/pip install -r requirements.txt
```

### Porta 5000 em uso

```bash
# Ver o que está usando a porta
sudo lsof -i :5000

# Matar processo
sudo kill -9 PID_DO_PROCESSO
```

### Nginx não funciona

```bash
# Testar configuração
sudo nginx -t

# Ver logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Firewall bloqueando

```bash
# Ver regras
sudo ufw status

# Permitir porta
sudo ufw allow 5000
sudo ufw allow 80
sudo ufw allow 443
```

## 📊 Monitoramento

### Recursos do sistema

```bash
# CPU e memória
htop

# Espaço em disco
df -h

# Logs do sistema
sudo journalctl -f
```

### Logs específicos

```bash
# Logs do painel
sudo tail -f /opt/nazuna-panel/logs/app.log

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Manutenção

### Backup automático

O backup é configurado automaticamente para rodar diariamente às 2h:

```bash
# Ver backups
ls -la /opt/nazuna-panel/backups/

# Backup manual
sudo /opt/nazuna-panel/backup.sh
```

### Atualizações

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Atualizar painel
cd /opt/nazuna-panel
sudo -u nazuna git pull
sudo systemctl restart nazuna-panel
```

### Limpeza

```bash
# Limpar logs antigos
sudo journalctl --vacuum-time=7d

# Limpar cache do apt
sudo apt autoremove -y
sudo apt autoclean
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `sudo journalctl -u nazuna-panel -f`
2. Verifique o status: `sudo systemctl status nazuna-panel`
3. Teste a conectividade: `curl http://localhost:5000`
4. Abra uma issue no GitHub com os logs

---

**✅ Instalação concluída! Seu Nazuna Panel está rodando em produção.**

