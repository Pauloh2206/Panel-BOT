import os
import subprocess
import signal
from flask import Blueprint, request, jsonify
from flask_socketio import emit
import threading
import time

bot_bp = Blueprint('bot', __name__)

# Variáveis globais para controle do processo do bot
bot_process = None
bot_status = "stopped"
nazuna_path = "/home/ubuntu/nazuna"

def get_bot_status():
    """Verifica o status atual do bot"""
    global bot_process, bot_status
    
    if bot_process is None:
        bot_status = "stopped"
        return bot_status
    
    # Verifica se o processo ainda está rodando
    try:
        if bot_process.poll() is None:
            bot_status = "running"
        else:
            bot_status = "stopped"
            bot_process = None
    except:
        bot_status = "stopped"
        bot_process = None
    
    return bot_status

def monitor_bot_process():
    """Monitor do processo do bot para emitir atualizações via WebSocket"""
    global bot_process, bot_status
    
    while bot_process and bot_process.poll() is None:
        time.sleep(1)
    
    # Processo terminou
    bot_status = "stopped"
    bot_process = None

@bot_bp.route('/status', methods=['GET'])
def status():
    """Retorna o status atual do bot"""
    current_status = get_bot_status()
    return jsonify({
        'status': current_status,
        'pid': bot_process.pid if bot_process else None
    })

@bot_bp.route('/start', methods=['POST'])
def start_bot():
    """Inicia o bot Nazuna"""
    global bot_process, bot_status
    
    try:
        # Verifica se o bot já está rodando
        if get_bot_status() == "running":
            return jsonify({
                'success': False,
                'message': 'Bot já está rodando'
            }), 400
        
        # Obtém configurações do request
        data = request.get_json() or {}
        mode = data.get('mode', 'normal')  # normal, dual, code
        
        # Prepara o comando baseado no modo
        if mode == 'dual':
            cmd = ['npm', 'run', 'start:dual']
        elif mode == 'code':
            cmd = ['npm', 'start', '--', '--code']
        else:
            cmd = ['npm', 'start']
        
        # Inicia o processo do bot
        bot_process = subprocess.Popen(
            cmd,
            cwd=nazuna_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        bot_status = "starting"
        
        # Inicia thread para monitorar o processo
        monitor_thread = threading.Thread(target=monitor_bot_process)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Bot iniciado em modo {mode}',
            'pid': bot_process.pid
        })
        
    except Exception as e:
        bot_status = "error"
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar o bot: {str(e)}'
        }), 500

@bot_bp.route('/stop', methods=['POST'])
def stop_bot():
    """Para o bot Nazuna"""
    global bot_process, bot_status
    
    try:
        if get_bot_status() == "stopped":
            return jsonify({
                'success': False,
                'message': 'Bot já está parado'
            }), 400
        
        if bot_process:
            # Tenta terminar graciosamente
            bot_process.terminate()
            
            # Aguarda um pouco para terminar graciosamente
            try:
                bot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Se não terminar graciosamente, força a parada
                bot_process.kill()
                bot_process.wait()
            
            bot_process = None
            bot_status = "stopped"
        
        return jsonify({
            'success': True,
            'message': 'Bot parado com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao parar o bot: {str(e)}'
        }), 500

@bot_bp.route('/restart', methods=['POST'])
def restart_bot():
    """Reinicia o bot Nazuna"""
    try:
        # Para o bot se estiver rodando
        if get_bot_status() == "running":
            stop_response = stop_bot()
            if not stop_response[0].get_json().get('success'):
                return stop_response
        
        # Aguarda um momento antes de reiniciar
        time.sleep(2)
        
        # Inicia o bot novamente
        return start_bot()
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao reiniciar o bot: {str(e)}'
        }), 500

@bot_bp.route('/logs', methods=['GET'])
def get_logs():
    """Retorna os logs do bot"""
    try:
        # Por enquanto, retorna logs básicos
        # Pode ser expandido para ler logs de arquivos específicos
        return jsonify({
            'logs': [
                {'timestamp': '2025-01-14 10:00:00', 'level': 'info', 'message': 'Bot iniciado'},
                {'timestamp': '2025-01-14 10:01:00', 'level': 'info', 'message': 'Conectado ao WhatsApp'},
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter logs: {str(e)}'
        }), 500

@bot_bp.route('/config', methods=['GET'])
def get_config():
    """Retorna a configuração atual do bot"""
    try:
        config_path = os.path.join(nazuna_path, 'dados', 'src', 'config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                import json
                config = json.load(f)
                return jsonify({
                    'success': True,
                    'config': config
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Arquivo de configuração não encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao ler configuração: {str(e)}'
        }), 500

@bot_bp.route('/config', methods=['POST'])
def update_config():
    """Atualiza a configuração do bot"""
    try:
        config_path = os.path.join(nazuna_path, 'dados', 'src', 'config.json')
        new_config = request.get_json()
        
        if not new_config:
            return jsonify({
                'success': False,
                'message': 'Configuração inválida'
            }), 400
        
        with open(config_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Configuração atualizada com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar configuração: {str(e)}'
        }), 500

