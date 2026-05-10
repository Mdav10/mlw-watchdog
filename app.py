from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>MLW Control</title>
    <style>
        body { background: #0a0e27; color: #00ffcc; font-family: monospace; padding: 20px; }
        h1 { color: #ff3366; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #00ffcc; padding: 8px; text-align: left; }
        th { background: #1a1f3a; }
        .login { max-width: 300px; margin: 100px auto; background: #1a1f3a; padding: 20px; }
        input, button { width: 100%; padding: 10px; margin: 5px 0; background: #0a0e27; color: #00ffcc; border: 1px solid #00ffcc; }
    </style>
    <script>
        async function checkAuth() {
            const res = await fetch('/api/auth');
            const data = await res.json();
            if (!data.authenticated) {
                document.getElementById('login').style.display = 'block';
                document.getElementById('content').style.display = 'none';
            } else {
                document.getElementById('login').style.display = 'none';
                document.getElementById('content').style.display = 'block';
                loadReports();
                setInterval(loadReports, 5000);
            }
        }
        async function login() {
            const pwd = document.getElementById('pwd').value;
            const res = await fetch('/api/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({password: pwd}) });
            const data = await res.json();
            if (data.success) checkAuth();
        }
        async function loadReports() {
            const res = await fetch('/api/reports');
            const data = await res.json();
            document.getElementById('reports').innerHTML = data.map(r => `<tr><td>${r.server_name}</td><td>${r.event_type}</td><td>${r.message}</td><td>${r.attacker_info || ''}</td><td>${r.created_at}</td></tr>`).join('');
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
    <h1>MLW Control - Watchdog Dashboard</h1>
    <table><thead><tr><th>Server</th><th>Event</th><th>Message</th><th>Attacker Info</th><th>Time</th></tr></thead><tbody id="reports"></tbody></table>
</div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML)

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

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO reports (server_name, ip_address, event_type, message, attacker_info) VALUES (%s, %s, %s, %s, %s)', (data.get('server'), request.remote_addr, data.get('event'), data.get('message'), data.get('attacker_info')))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/reports')
def get_reports():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT server_name, event_type, message, attacker_info, created_at FROM reports ORDER BY created_at DESC LIMIT 100')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'server_name': r[0], 'event_type': r[1], 'message': r[2], 'attacker_info': r[3], 'created_at': r[4]} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
