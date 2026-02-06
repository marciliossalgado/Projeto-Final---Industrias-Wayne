import sqlite3
from werkzeug.security import generate_password_hash

DB = 'security.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        status TEXT,
        location TEXT
    )
    ''')

    users = [
        ('admin', generate_password_hash('adminpass')),
        ('manager', generate_password_hash('managerpass')),
        ('staff', generate_password_hash('staffpass')),
    ]
    roles = ['admin', 'manager', 'employee']
    for (u, p), r in zip(users, roles):
        try:
            c.execute('INSERT INTO users (username, password, role) VALUES (?,?,?)', (u, p, r))
        except Exception:
            pass

    resources = [
        ('Câmera A1', 'Câmera', 'Operacional', 'Portão Norte'),
        ('Veículo V12', 'Veículo', 'Manutenção', 'Garagem'),
        ('Rádio R3', 'Comunicação', 'Operacional', 'Central'),
    ]
    for r in resources:
        try:
            c.execute('INSERT INTO resources (name, type, status, location) VALUES (?,?,?,?)', r)
        except Exception:
            pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Banco de dados inicializado: security.db')
