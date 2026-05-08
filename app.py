import os
import subprocess
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Global state
is_running = False
logs = []
log_lock = threading.Lock()
current_process = None

# Configuration
DATA_DIR = Path("/app/data")
URLS_FILE = Path("/app/urls.txt")
COOKIES_FILE = Path("/app/cookies.txt")
DIRECT_URLS_FILE = Path("/app/direct_urls.txt")

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

def run_download_job(urls_text, cookies_text):
    global is_running, current_process, logs
    
    try:
        # Save URLs
        URLS_FILE.write_text(urls_text)
        
        # Save cookies if provided
        if cookies_text and cookies_text.strip():
            COOKIES_FILE.write_text(cookies_text)
        elif COOKIES_FILE.exists():
            COOKIES_FILE.unlink()
        
        # Run the bash script
        process = subprocess.Popen(
            ['bash', 'd.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd="/app"
        )
        current_process = process
        
        # Capture output line by line
        for line in iter(process.stdout.readline, ''):
            line = line.rstrip()
            with log_lock:
                logs.append(line)
                if len(logs) > 100000:
                    logs.pop(0)
            print(line)
        
        process.wait()
        
        with log_lock:
            if process.returncode == 0:
                logs.append("=== Job completed successfully ===")
            else:
                logs.append(f"=== Job failed with exit code {process.returncode} ===")
    
    except Exception as e:
        with log_lock:
            logs.append(f"ERROR: {str(e)}")
    finally:
        is_running = False
        current_process = None

def run_direct_download_job(direct_urls_text):
    global is_running, current_process, logs
    
    try:
        # Save direct URLs
        DIRECT_URLS_FILE.write_text(direct_urls_text)
        
        # Run the direct download script
        process = subprocess.Popen(
            ['bash', 'd-direct.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd="/app"
        )
        current_process = process
        
        for line in iter(process.stdout.readline, ''):
            line = line.rstrip()
            with log_lock:
                logs.append(line)
                if len(logs) > 2000:
                    logs.pop(0)
            print(line)
        
        process.wait()
        
        with log_lock:
            if process.returncode == 0:
                logs.append("=== Direct download job completed successfully ===")
            else:
                logs.append(f"=== Direct download job failed with exit code {process.returncode} ===")
    
    except Exception as e:
        with log_lock:
            logs.append(f"ERROR: {str(e)}")
    finally:
        is_running = False
        current_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_job():
    global is_running
    
    if is_running:
        return jsonify({'error': 'A download job is already running'}), 409
    
    data = request.json
    job_type = data.get('type', 'youtube')
    
    if job_type == 'youtube':
        urls = data.get('urls', '').strip()
        cookies = data.get('cookies', '')
        
        if not urls:
            return jsonify({'error': 'YouTube URLs are required'}), 400
        
        with log_lock:
            logs.clear()
            logs.append(f"=== Starting YouTube job at {time.ctime()} ===")
        
        is_running = True
        thread = threading.Thread(target=run_download_job, args=(urls, cookies))
        thread.daemon = True
        thread.start()
        
    elif job_type == 'direct':
        urls = data.get('urls', '').strip()
        
        if not urls:
            return jsonify({'error': 'File URLs are required'}), 400
        
        with log_lock:
            logs.clear()
            logs.append(f"=== Starting direct download job at {time.ctime()} ===")
        
        is_running = True
        thread = threading.Thread(target=run_direct_download_job, args=(urls,))
        thread.daemon = True
        thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_job():
    global current_process, is_running
    
    if not is_running:
        return jsonify({'error': 'No job is running'}), 400
    
    if current_process:
        current_process.terminate()
        with log_lock:
            logs.append("=== Terminating job... ===")
        return jsonify({'status': 'stopping'})
    
    return jsonify({'error': 'No process found'}), 400

@app.route('/api/status')
def get_status():
    offset = int(request.args.get('offset', 0))
    
    with log_lock:
        new_logs = logs[offset:] if offset < len(logs) else []
        return jsonify({
            'logs': new_logs,
            'offset': len(logs),
            'running': is_running
        })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'running': is_running})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
