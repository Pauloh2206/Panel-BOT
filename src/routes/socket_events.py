from flask_socketio import emit, disconnect
import threading
import time

def register_socket_events(socketio):
    """Registra todos os eventos SocketIO"""
    
    @socketio.on('connect')
    def handle_connect():
        """Cliente conectado"""
        print('Cliente conectado')
        emit('connected', {'message': 'Conectado ao servidor'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Cliente desconectado"""
        print('Cliente desconectado')
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Cliente entra em uma sala"""
        room = data.get('room', 'default')
        # join_room(room)
        emit('joined_room', {'room': room})
    
    @socketio.on('bot_status_request')
    def handle_bot_status_request():
        """Cliente solicita status do bot"""
        from src.routes.bot import get_bot_status, bot_process
        
        status = get_bot_status()
        emit('bot_status_update', {
            'status': status,
            'pid': bot_process.pid if bot_process else None
        })
    
    @socketio.on('terminal_input')
    def handle_terminal_input(data):
        """Recebe input do terminal do cliente"""
        session_id = data.get('session_id', 'default')
        input_data = data.get('input', '')
        
        # Aqui você integraria com o sistema de terminal
        # Por enquanto, apenas echo
        emit('terminal_output', {
            'session_id': session_id,
            'data': f'Echo: {input_data}\n'
        })
    
    @socketio.on('start_bot_monitoring')
    def handle_start_bot_monitoring():
        """Inicia monitoramento do bot em tempo real"""
        def monitor_bot():
            while True:
                from src.routes.bot import get_bot_status, bot_process
                
                status = get_bot_status()
                socketio.emit('bot_status_update', {
                    'status': status,
                    'pid': bot_process.pid if bot_process else None,
                    'timestamp': time.time()
                })
                
                time.sleep(5)  # Atualiza a cada 5 segundos
        
        # Inicia thread de monitoramento
        monitor_thread = threading.Thread(target=monitor_bot)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        emit('monitoring_started', {'message': 'Monitoramento iniciado'})
    
    @socketio.on('get_system_info')
    def handle_get_system_info():
        """Retorna informações do sistema"""
        import psutil
        import os
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'uptime': time.time() - psutil.boot_time()
            }
            
            emit('system_info', system_info)
            
        except Exception as e:
            emit('error', {'message': f'Erro ao obter informações do sistema: {str(e)}'})
    
    @socketio.on('ping')
    def handle_ping():
        """Responde a ping do cliente"""
        emit('pong', {'timestamp': time.time()})
    
    return socketio

