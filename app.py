from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from datetime import datetime
import json
import os
import humanize
import mimetypes


os.system('python -m pip install -r requirements.txt')
os.system('start http://10.189.221.71:8000')

app = Flask(__name__, template_folder='web')

# 存储留言的列表
messages = []

# 确保数据持久化
def load_messages():
    global messages
    if os.path.exists('messages.json'):
        with open('messages.json', 'r', encoding='utf-8') as f:
            messages = json.load(f)

def save_messages():
    with open('messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# 加载现有留言
load_messages()

# 文件上传配置
UPLOAD_FOLDER = 'files'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
    'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'mp3',
    'ppt', 'pptx', '7z'
}

# 文件类型分类
FILE_CATEGORIES = {
    '学习文件': ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
    '图片': ['png', 'jpg', 'jpeg', 'gif'],
    '音频': ['mp3'],
    '视频': ['mp4'],
    '压缩包': ['zip', 'rar', '7z']
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    # 移除不安全的字符
    filename = filename.replace(' ', '_')
    filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
    return filename

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return '其他'

def get_file_info(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        stats = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(filename)
        return {
            'name': filename,
            'size': humanize.naturalsize(stats.st_size),
            'time': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'category': get_file_category(filename),
            'mime_type': mime_type or 'application/octet-stream'
        }
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/message-board')
def message_board():
    return render_template('message_board.html', messages=messages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/files')
def files():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            file_info = get_file_info(filename)
            if file_info:
                if category and file_info['category'] != category:
                    continue
                if search and search.lower() not in filename.lower():
                    continue
                files.append(file_info)
    
    files.sort(key=lambda x: x['time'], reverse=True)
    return render_template('files.html', files=files, categories=FILE_CATEGORIES.keys(), current_category=category)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 如果文件已存在，添加时间戳
        if os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(file_path)
        return jsonify({'success': True, 'filename': filename}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/preview/<filename>')
def preview_file(filename):
    file_info = get_file_info(filename)
    if not file_info:
        return "文件不存在", 404
    
    if file_info['mime_type'].startswith('image/'):
        return render_template('preview.html', file_info=file_info, preview_type='image')
    elif file_info['mime_type'] == 'application/pdf':
        return render_template('preview.html', file_info=file_info, preview_type='pdf')
    else:
        return render_template('preview.html', file_info=file_info, preview_type='text')

@app.route('/add_message', methods=['POST'])
def add_message():
    name = request.form.get('name')
    content = request.form.get('message')
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if name and content:
        messages.append({
            'name': name,
            'content': content,
            'time': time
        })
        save_messages()
    
    return redirect(url_for('message_board'))

@app.route('/more')
def more():
    return render_template('more.html')

@app.route('/static/img/favicon.ico')
def favicon():
    return send_from_directory('static', 'img/favicon.ico')



if __name__ == '__main__':
    # 确保上传文件夹存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0', port=8000) 
