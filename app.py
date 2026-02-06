from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
DB = os.environ.get('DB_PATH', 'security.db')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return wrapper

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Credenciais inválidas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/resources')
@login_required
def resources_page():
    return render_template('resources.html')

@app.route('/users')
@login_required
@role_required('admin')
def users_page():
    conn = get_db()
    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/api/resources', methods=['GET'])
@login_required
def api_get_resources():
    conn = get_db()
    rows = conn.execute('SELECT * FROM resources').fetchall()
    conn.close()
    resources = [dict(r) for r in rows]
    return jsonify(resources)


@app.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    conn = get_db()
    total_resources = conn.execute('SELECT COUNT(*) as c FROM resources').fetchone()['c']
    types = conn.execute('SELECT type, COUNT(*) as c FROM resources GROUP BY type').fetchall()
    status = conn.execute('SELECT status, COUNT(*) as c FROM resources GROUP BY status').fetchall()
    users = conn.execute('SELECT role, COUNT(*) as c FROM users GROUP BY role').fetchall()
    conn.close()
    return jsonify({
        'total_resources': total_resources,
        'resources_by_type': {r['type'] if r['type'] else 'unknown': r['c'] for r in types},
        'resources_by_status': {r['status'] if r['status'] else 'unknown': r['c'] for r in status},
        'users_by_role': {u['role']: u['c'] for u in users}
    })

@app.route('/api/resources', methods=['POST'])
@login_required
@role_required('admin', 'manager')
def api_add_resource():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO resources(name, type, status, location) VALUES (?,?,?,?)',
                 (data.get('name'), data.get('type'), data.get('status'), data.get('location')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/resources/<int:res_id>', methods=['PUT'])
@login_required
@role_required('admin', 'manager')
def api_update_resource(res_id):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE resources SET name=?, type=?, status=?, location=? WHERE id=?',
                 (data.get('name'), data.get('type'), data.get('status'), data.get('location'), res_id))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/resources/<int:res_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_delete_resource(res_id):
    conn = get_db()
    conn.execute('DELETE FROM resources WHERE id=?', (res_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True)
