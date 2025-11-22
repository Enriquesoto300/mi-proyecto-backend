import os
import pymysql
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('localhost'),
        user=os.getenv('root'),
        password=os.getenv('toor'),
        database=os.getenv('University'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return "Servidor de Autenticación Activo"

# --- ENDPOINT 1: REGISTRO DE USUARIO ---
@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.json
    # Datos requeridos: nombre, apellido, email, password, tipo, identificador (matricula/empleado), carrera_id (si es alumno)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Validar si el email ya existe
            cursor.execute("SELECT usuario_id FROM Usuarios WHERE email = %s", (data['email'],))
            if cursor.fetchone():
                return jsonify({"error": "El correo ya está registrado"}), 400

            # 2. Encriptar contraseña
            hashed_password = generate_password_hash(data['password'])
            
            alumno_id = None
            profesor_id = None
            personal_id = None

            # 3. Insertar en la tabla de perfil correspondiente primero
            if data['tipo'] == 'alumno':
                # Nota: Asumimos carrera_id=1 para la demo si no se envía
                sql_perfil = "INSERT INTO Alumnos (primer_nombre, apellido_paterno, matricula, carrera_id) VALUES (%s, %s, %s, 1)"
                cursor.execute(sql_perfil, (data['nombre'], data['apellido'], data['identificador']))
                alumno_id = cursor.lastrowid
                
            elif data['tipo'] == 'profesor':
                sql_perfil = "INSERT INTO Profesores (primer_nombre, apellido_paterno, empleado_id) VALUES (%s, %s, %s)"
                cursor.execute(sql_perfil, (data['nombre'], data['apellido'], data['identificador']))
                profesor_id = cursor.lastrowid
                
            elif data['tipo'] == 'administrativo':
                sql_perfil = "INSERT INTO PersonalAdministrativo (primer_nombre, apellido_paterno, empleado_id, cargo) VALUES (%s, %s, %s, 'Juez')"
                cursor.execute(sql_perfil, (data['nombre'], data['apellido'], data['identificador']))
                personal_id = cursor.lastrowid

            # 4. Crear el Usuario vinculado al perfil
            sql_usuario = """
                INSERT INTO Usuarios (email, password_hash, tipo, alumno_id, profesor_id, personal_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (data['email'], hashed_password, data['tipo'], alumno_id, profesor_id, personal_id))
            
            conn.commit()
            return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
            
    except Exception as e:
        conn.rollback() # Si algo falla, deshacemos todo
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- ENDPOINT 2: LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Buscamos al usuario por email
            sql = "SELECT * FROM Usuarios WHERE email = %s"
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario['password_hash'], password):
                # Login Exitoso: Devolvemos sus datos clave (sin la contraseña)
                return jsonify({
                    "mensaje": "Login exitoso",
                    "usuario_id": usuario['usuario_id'],
                    "tipo": usuario['tipo'],
                    "email": usuario['email']
                }), 200
            else:
                return jsonify({"error": "Credenciales incorrectas"}), 401
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)