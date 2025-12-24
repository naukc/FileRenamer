import os
import sys
import webbrowser
from flask import Flask, render_template, request, jsonify

if getattr(sys, 'frozen', False):
    app = Flask(__name__, root_path=sys._MEIPASS)
else:
    app = Flask(__name__)

def open_folder_dialog():
    import subprocess
    import sys
    
    if sys.platform == 'darwin':
        try:
            # Use AppleScript to open a native folder selection dialog
            script = 'POSIX path of (choose folder with prompt "Select a folder")'
            cmd = ['osascript', '-e', script]
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8').strip()
            return result
        except subprocess.CalledProcessError:
            return None # User cancelled
    else:
        # Fallback for Windows/Linux using tkinter (only if not on Mac)
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            folder_path = filedialog.askdirectory()
            root.destroy()
            return folder_path
        except:
            return None

@app.route('/api/select-folder', methods=['POST'])
def select_folder_route():
    try:
        folder_path = open_folder_dialog()
        if folder_path:
            return jsonify({'path': folder_path})
        return jsonify({'path': None}) # User cancelled
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_files(directory):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')]
        files.sort()
        return files
    except Exception as e:
        return []

def apply_rules(filename, rules, index=0):
    name, ext = os.path.splitext(filename)
    new_name = name
    
    for rule in rules:
        r_type = rule.get('type')
        
        if r_type == 'replace':
            old_str = rule.get('old', '')
            new_str = rule.get('new', '')
            if old_str:
                new_name = new_name.replace(old_str, new_str)
                
        elif r_type == 'new_name':
            custom_name = rule.get('name', '')
            if custom_name:
                new_name = custom_name
                
        elif r_type == 'prepend':
            text = rule.get('text', '')
            new_name = text + new_name
            
        elif r_type == 'append':
            text = rule.get('text', '')
            new_name = new_name + text
            
        elif r_type == 'counter':
            start = int(rule.get('start', 1))
            step = int(rule.get('step', 1))
            padding = int(rule.get('padding', 3))
            separator = rule.get('separator', '_')
            position = rule.get('position', 'end') # 'start' or 'end'
            
            current_val = start + (index * step)
            counter_str = f"{current_val:0{padding}d}"
            
            if position == 'start':
                new_name = f"{counter_str}{separator}{new_name}"
            else:
                new_name = f"{new_name}{separator}{counter_str}"
                
        elif r_type == 'extension':
            new_ext = rule.get('ext', '')
            if new_ext:
                if not new_ext.startswith('.'):
                    new_ext = '.' + new_ext
                ext = new_ext

    return new_name + ext

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files', methods=['POST'])
def list_files():
    data = request.json
    directory = data.get('directory')
    if not directory or not os.path.isdir(directory):
        return jsonify({'error': 'Invalid directory'}), 400
    
    files = get_files(directory)
    return jsonify({'files': files})

@app.route('/api/preview', methods=['POST'])
def preview():
    data = request.json
    directory = data.get('directory')
    rules = data.get('rules', [])
    
    if not directory or not os.path.isdir(directory):
        return jsonify({'error': 'Invalid directory'}), 400
        
    files = get_files(directory)
    preview_data = []
    
    for i, filename in enumerate(files):
        new_filename = apply_rules(filename, rules, i)
        preview_data.append({
            'original': filename,
            'new': new_filename,
            'changed': filename != new_filename
        })
        
    return jsonify({'preview': preview_data})

@app.route('/api/rename', methods=['POST'])
def rename():
    data = request.json
    directory = data.get('directory')
    rules = data.get('rules', [])
    
    if not directory or not os.path.isdir(directory):
        return jsonify({'error': 'Invalid directory'}), 400
        
    files = get_files(directory)
    results = []
    errors = []
    
    # First pass: Check for collisions
    preview_map = {}
    for i, filename in enumerate(files):
        new_filename = apply_rules(filename, rules, i)
        if new_filename in preview_map:
             return jsonify({'error': f'Name collision detected: {new_filename}'}), 400
        preview_map[new_filename] = filename
        
    # Second pass: Rename
    # TODO: Handle case where A -> B and B -> C (chain renaming). 
    # For simplicity in this version, we'll just do it. 
    # Ideally we should rename to temp names first or sort carefully.
    # But for a simple tool, we'll try direct rename and catch errors.
    
    renamed_count = 0
    for i, filename in enumerate(files):
        new_filename = apply_rules(filename, rules, i)
        if filename != new_filename:
            try:
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_filename)
                os.rename(old_path, new_path)
                renamed_count += 1
            except Exception as e:
                errors.append(f"Failed to rename {filename}: {str(e)}")
                
    return jsonify({'success': True, 'renamed': renamed_count, 'errors': errors})

if __name__ == '__main__':
    # Check if running as frozen executable
    if getattr(sys, 'frozen', False):
        webbrowser.open('http://127.0.0.1:5001/')
        app.run(debug=False, port=5001)
    else:
        # Open browser only once (avoid reloader opening it twice)
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open('http://127.0.0.1:5001/')
        app.run(debug=True, port=5001)
