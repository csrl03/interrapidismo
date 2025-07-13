import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'supersecretkey2025!'

# --- Inicialización de la base de datos ---
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    # Tabla de usuarios (ahora con campo password_hash)
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('cliente', 'admin')),
            rastreos_asociados TEXT
        )
    ''')
    # Tabla de rastreos
    c.execute('''
        CREATE TABLE IF NOT EXISTS rastreos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_guia TEXT NOT NULL,
            documento TEXT NOT NULL,
            admision TEXT,
            estimada TEXT,
            destino_ciudad TEXT,
            destino_nombre TEXT,
            destino_direccion TEXT,
            origen_ciudad TEXT,
            origen_nombre TEXT,
            origen_direccion TEXT,
            origen_telefono TEXT,
            empaque TEXT,
            actualizaciones TEXT
        )
    ''')
    # Crear usuario admin si no existe
    c.execute('SELECT * FROM usuarios WHERE nombre_usuario = ?', ('admin',))
    if not c.fetchone():
        admin_pass = generate_password_hash('AdminClaveSegura2025!')
        c.execute('INSERT INTO usuarios (nombre_usuario, password_hash, rol, rastreos_asociados) VALUES (?, ?, ?, ?)',
                  ('admin', admin_pass, 'admin', ''))
    conn.commit()
    conn.close()

init_db()

# --- Endpoint de login con JWT ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    nombre = data.get('nombre_usuario')
    password = data.get('password')
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT password_hash, rol FROM usuarios WHERE nombre_usuario = ?', (nombre,))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        token = jwt.encode({
            'usuario': nombre,
            'rol': row[1],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm='HS256')
        return jsonify({'status': 'ok', 'rol': row[1], 'token': token})
    else:
        return jsonify({'error': 'Credenciales incorrectas'}), 401

# --- Decorador para proteger endpoints ---
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[-1]
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.usuario = data['usuario']
            request.rol = data['rol']
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        return f(*args, **kwargs)
    return decorated

# --- Endpoints de usuarios ---
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    nombre = data.get('nombre_usuario')
    password = data.get('password')
    rol = data.get('rol')
    rastreos = data.get('rastreos_asociados', '')
    password_hash = generate_password_hash(password)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios (nombre_usuario, password_hash, rol, rastreos_asociados) VALUES (?, ?, ?, ?)', (nombre, password_hash, rol, rastreos))
        conn.commit()
        return jsonify({'status': 'ok'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Usuario ya existe'}), 400
    finally:
        conn.close()

@app.route('/usuarios/<nombre_usuario>', methods=['GET'])
def obtener_usuario(nombre_usuario):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({
            'id': row[0],
            'nombre_usuario': row[1],
            'rol': row[2],
            'rastreos_asociados': row[3]
        })
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

# --- Endpoints protegidos ---
@app.route('/rastreos', methods=['POST'])
@token_required
def crear_rastreo():
    data = request.json
    campos = [
        'numero_guia', 'documento', 'admision', 'estimada', 'destino_ciudad', 'destino_nombre',
        'destino_direccion', 'origen_ciudad', 'origen_nombre', 'origen_direccion',
        'origen_telefono', 'empaque', 'actualizaciones'
    ]
    valores = [data.get(campo) for campo in campos]
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO rastreos (numero_guia, documento, admision, estimada, destino_ciudad, destino_nombre, destino_direccion, origen_ciudad, origen_nombre, origen_direccion, origen_telefono, empaque, actualizaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', valores)
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'}), 201

@app.route('/rastreos/<documento>', methods=['GET'])
def obtener_rastreos_por_documento(documento):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM rastreos WHERE documento = ?', (documento,))
    rows = c.fetchall()
    conn.close()
    rastreos = []
    for row in rows:
        rastreos.append({
            'id': row[0],
            'numero_guia': row[1],
            'documento': row[2],
            'admision': row[3],
            'estimada': row[4],
            'destino_ciudad': row[5],
            'destino_nombre': row[6],
            'destino_direccion': row[7],
            'origen_ciudad': row[8],
            'origen_nombre': row[9],
            'origen_direccion': row[10],
            'origen_telefono': row[11],
            'empaque': row[12],
            'actualizaciones': row[13]
        })
    return jsonify(rastreos)

@app.route('/rastreos/actualizacion/<int:id_rastreo>', methods=['PUT'])
@token_required
def actualizar_actualizaciones(id_rastreo):
    data = request.json
    actualizaciones = data.get('actualizaciones')
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('UPDATE rastreos SET actualizaciones = ? WHERE id = ?', (actualizaciones, id_rastreo))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/rastreos/actualizacion/<int:id_rastreo>', methods=['DELETE'])
@token_required
def eliminar_rastreo(id_rastreo):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('DELETE FROM rastreos WHERE id = ?', (id_rastreo,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
