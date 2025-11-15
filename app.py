from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Esto permite que CUALQUIER sitio web acceda a tu backend (Inseguro para bancos, perfecto para esta tarea)
CORS(app) 

@app.route('/')
def home():
    return "¡El servidor backend está vivo y funcionando!"

@app.route('/api/saludo')
def saludo():
    # Aquí es donde más tarde consultarás la Base de Datos
    datos = {
        "mensaje": "Hola desde el Backend (Python)",
        "estudiante": "Tu Nombre",
        "estado": "Conexión Exitosa"
    }
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)