import os
import subprocess
import threading
import time
from flask import Blueprint, request, jsonify
from flask_socketio import emit

terminal_bp = Blueprint('terminal', __name__)

# Dicionário para armazenar sessões de terminal ativas
terminal_sessions = {}

class TerminalSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.master_fd = None
        self.slave_fd = None
        self.process = None
        self.thread = None
        self.active = False
    
    def start(self):
        """Inicia uma nova sessão de terminal"""
        try:
            # Cria um pseudo-terminal
            self.master_fd, self.slave_fd = pty.openpty()
            
            # Configura o terminal
            attrs = termios.tcgetattr(self.slave_fd)
            attrs[1] = attrs[1] & ~termios.OPOST  # Disable output processing
            termios.tcsetattr(self.slave_fd, termios.TCSANOW, attrs)
            
            # Inicia o shell
            self.process = subprocess.Popen(
                ['/bin/bash'],
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid
            )
            
            self.active = True
            
            # Inicia thread para ler a saída
            self.thread = threading.Thread(target=self._read_output)
            self.thread.daemon = True
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"Erro ao iniciar terminal: {e}")
            return False
    
    def _read_output(self):
        """Lê a saída do terminal e envia via WebSocket"""
        while self.active and self.process.poll() is None:
            try:
                # Verifica se há dados para ler
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                
                if ready:
                    data = os.read(self.master_fd, 1024)
                    if data:
                        output = data.decode('utf-8', errors='ignore')
                        # Aqui você emitiria via SocketIO
                        # emit('terminal_output', {'session_id': self.session_id, 'data': output})
                        
            except Exception as e:
                print(f"Erro ao ler saída do terminal: {e}")
                break
    
    def write_input(self, data):
        """Escreve dados no terminal"""
        try:
            if self.master_fd and self.active:
                os.write(self.master_fd, data.encode('utf-8'))
                return True
        except Exception as e:
            print(f"Erro ao escrever no terminal: {e}")
        return False
    
    def resize(self, rows, cols):
        """Redimensiona o terminal"""
        try:
            if self.master_fd:
                winsize = struct.pack('HHHH', rows, cols, 0, 0)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
                return True
        except Exception as e:
            print(f"Erro ao redimensionar terminal: {e}")
        return False
    
    def close(self):
        """Fecha a sessão do terminal"""
        self.active = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass
        
        if self.slave_fd:
            try:
                os.close(self.slave_fd)
            except:
                pass

@terminal_bp.route('/create', methods=['POST'])
def create_terminal():
    """Cria uma nova sessão de terminal"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        
        # Remove sessão existente se houver
        if session_id in terminal_sessions:
            terminal_sessions[session_id].close()
        
        # Cria nova sessão
        session = TerminalSession(session_id)
        if session.start():
            terminal_sessions[session_id] = session
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Terminal criado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao criar terminal'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar terminal: {str(e)}'
        }), 500

@terminal_bp.route('/execute', methods=['POST'])
def execute_command():
    """Executa um comando no terminal"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({
                'success': False,
                'message': 'Comando não fornecido'
            }), 400
        
        command = data['command']
        session_id = data.get('session_id', 'default')
        
        # Executa comando simples (sem sessão persistente)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/home/ubuntu'
            )
            
            return jsonify({
                'success': True,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'message': 'Comando expirou (timeout de 30s)'
            }), 408
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao executar comando: {str(e)}'
        }), 500

@terminal_bp.route('/input', methods=['POST'])
def send_input():
    """Envia input para uma sessão de terminal"""
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({
                'success': False,
                'message': 'Input não fornecido'
            }), 400
        
        input_data = data['input']
        session_id = data.get('session_id', 'default')
        
        if session_id not in terminal_sessions:
            return jsonify({
                'success': False,
                'message': 'Sessão de terminal não encontrada'
            }), 404
        
        session = terminal_sessions[session_id]
        if session.write_input(input_data):
            return jsonify({
                'success': True,
                'message': 'Input enviado'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao enviar input'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar input: {str(e)}'
        }), 500

@terminal_bp.route('/resize', methods=['POST'])
def resize_terminal():
    """Redimensiona uma sessão de terminal"""
    try:
        data = request.get_json()
        if not data or 'rows' not in data or 'cols' not in data:
            return jsonify({
                'success': False,
                'message': 'Dimensões não fornecidas'
            }), 400
        
        rows = data['rows']
        cols = data['cols']
        session_id = data.get('session_id', 'default')
        
        if session_id not in terminal_sessions:
            return jsonify({
                'success': False,
                'message': 'Sessão de terminal não encontrada'
            }), 404
        
        session = terminal_sessions[session_id]
        if session.resize(rows, cols):
            return jsonify({
                'success': True,
                'message': 'Terminal redimensionado'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao redimensionar terminal'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao redimensionar terminal: {str(e)}'
        }), 500

@terminal_bp.route('/close', methods=['POST'])
def close_terminal():
    """Fecha uma sessão de terminal"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        
        if session_id in terminal_sessions:
            terminal_sessions[session_id].close()
            del terminal_sessions[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Terminal fechado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao fechar terminal: {str(e)}'
        }), 500

@terminal_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """Lista as sessões de terminal ativas"""
    try:
        active_sessions = []
        for session_id, session in terminal_sessions.items():
            if session.active:
                active_sessions.append({
                    'session_id': session_id,
                    'pid': session.process.pid if session.process else None
                })
        
        return jsonify({
            'success': True,
            'sessions': active_sessions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar sessões: {str(e)}'
        }), 500

