import os
import shutil
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename
import mimetypes

files_bp = Blueprint('files', __name__)

# Diretório base para operações de arquivo (restrito ao projeto Nazuna)
BASE_DIR = "/home/ubuntu/nazuna"
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Criar diretório de upload se não existir
os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_safe_path(path):
    """Verifica se o caminho está dentro do diretório permitido"""
    try:
        real_path = os.path.realpath(path)
        real_base = os.path.realpath(BASE_DIR)
        return real_path.startswith(real_base)
    except:
        return False

@files_bp.route('/list', methods=['GET'])
def list_files():
    """Lista arquivos e diretórios"""
    try:
        path = request.args.get('path', '')
        full_path = os.path.join(BASE_DIR, path.lstrip('/'))
        
        if not is_safe_path(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não permitido'
            }), 403
        
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não encontrado'
            }), 404
        
        items = []
        
        # Adiciona item para voltar ao diretório pai (se não estiver na raiz)
        if path and path != '/':
            parent_path = os.path.dirname(path.rstrip('/'))
            items.append({
                'name': '..',
                'type': 'directory',
                'path': parent_path,
                'size': 0,
                'modified': None
            })
        
        # Lista itens do diretório
        for item in sorted(os.listdir(full_path)):
            if item.startswith('.'):  # Pula arquivos ocultos
                continue
                
            item_path = os.path.join(full_path, item)
            relative_path = os.path.join(path, item).replace('\\', '/')
            
            try:
                stat = os.stat(item_path)
                
                items.append({
                    'name': item,
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'path': relative_path,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
            except:
                continue
        
        return jsonify({
            'success': True,
            'path': path,
            'items': items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar arquivos: {str(e)}'
        }), 500

@files_bp.route('/read', methods=['GET'])
def read_file():
    """Lê o conteúdo de um arquivo"""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({
                'success': False,
                'message': 'Caminho não fornecido'
            }), 400
        
        full_path = os.path.join(BASE_DIR, path.lstrip('/'))
        
        if not is_safe_path(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não permitido'
            }), 403
        
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'message': 'Arquivo não encontrado'
            }), 404
        
        if os.path.isdir(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho é um diretório'
            }), 400
        
        # Verifica o tipo de arquivo
        mime_type, _ = mimetypes.guess_type(full_path)
        
        # Só permite ler arquivos de texto
        if mime_type and not mime_type.startswith('text/'):
            return jsonify({
                'success': False,
                'message': 'Tipo de arquivo não suportado para leitura'
            }), 400
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Tenta com encoding latin-1 se UTF-8 falhar
            with open(full_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'path': path,
            'size': len(content)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao ler arquivo: {str(e)}'
        }), 500

@files_bp.route('/write', methods=['POST'])
def write_file():
    """Escreve conteúdo em um arquivo"""
    try:
        data = request.get_json()
        if not data or 'path' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'Caminho ou conteúdo não fornecido'
            }), 400
        
        path = data['path']
        content = data['content']
        
        full_path = os.path.join(BASE_DIR, path.lstrip('/'))
        
        if not is_safe_path(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não permitido'
            }), 403
        
        # Cria diretórios pai se necessário
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'message': 'Arquivo salvo com sucesso',
            'path': path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar arquivo: {str(e)}'
        }), 500

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Faz upload de um arquivo"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo fornecido'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo selecionado'
            }), 400
        
        # Obtém o caminho de destino
        dest_path = request.form.get('path', '')
        
        # Sanitiza o nome do arquivo
        filename = secure_filename(file.filename)
        
        # Caminho completo de destino
        if dest_path:
            full_dest_path = os.path.join(BASE_DIR, dest_path.lstrip('/'))
        else:
            full_dest_path = UPLOAD_DIR
        
        if not is_safe_path(full_dest_path):
            return jsonify({
                'success': False,
                'message': 'Caminho de destino não permitido'
            }), 403
        
        # Cria diretório se não existir
        os.makedirs(full_dest_path, exist_ok=True)
        
        # Caminho final do arquivo
        file_path = os.path.join(full_dest_path, filename)
        
        # Salva o arquivo
        file.save(file_path)
        
        # Caminho relativo para retorno
        relative_path = os.path.relpath(file_path, BASE_DIR)
        
        return jsonify({
            'success': True,
            'message': 'Arquivo enviado com sucesso',
            'path': relative_path,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao fazer upload: {str(e)}'
        }), 500

@files_bp.route('/download', methods=['GET'])
def download_file():
    """Faz download de um arquivo"""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({
                'success': False,
                'message': 'Caminho não fornecido'
            }), 400
        
        full_path = os.path.join(BASE_DIR, path.lstrip('/'))
        
        if not is_safe_path(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não permitido'
            }), 403
        
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'message': 'Arquivo não encontrado'
            }), 404
        
        if os.path.isdir(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho é um diretório'
            }), 400
        
        return send_file(full_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao fazer download: {str(e)}'
        }), 500

@files_bp.route('/delete', methods=['DELETE'])
def delete_file():
    """Deleta um arquivo ou diretório"""
    try:
        data = request.get_json()
        if not data or 'path' not in data:
            return jsonify({
                'success': False,
                'message': 'Caminho não fornecido'
            }), 400
        
        path = data['path']
        full_path = os.path.join(BASE_DIR, path.lstrip('/'))
        
        if not is_safe_path(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não permitido'
            }), 403
        
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'message': 'Arquivo/diretório não encontrado'
            }), 404
        
        # Proteção contra deleção de arquivos importantes
        protected_files = ['package.json', 'connect.js', 'index.js']
        if os.path.basename(full_path) in protected_files:
            return jsonify({
                'success': False,
                'message': 'Arquivo protegido não pode ser deletado'
            }), 403
        
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        
        return jsonify({
            'success': True,
            'message': 'Arquivo/diretório deletado com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar: {str(e)}'
        }), 500

@files_bp.route('/create-folder', methods=['POST'])
def create_folder():
    """Cria um novo diretório"""
    try:
        data = request.get_json()
        if not data or 'path' not in data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Caminho ou nome não fornecido'
            }), 400
        
        path = data['path']
        name = secure_filename(data['name'])
        
        full_path = os.path.join(BASE_DIR, path.lstrip('/'), name)
        
        if not is_safe_path(full_path):
            return jsonify({
                'success': False,
                'message': 'Caminho não permitido'
            }), 403
        
        if os.path.exists(full_path):
            return jsonify({
                'success': False,
                'message': 'Diretório já existe'
            }), 400
        
        os.makedirs(full_path)
        
        return jsonify({
            'success': True,
            'message': 'Diretório criado com sucesso',
            'path': os.path.join(path, name)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar diretório: {str(e)}'
        }), 500

