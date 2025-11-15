from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORS permite que CUALQUIER sitio web acceda al backend
CORS(app) 

@app.route('/')
def home():
    return "¡El servidor backend está vivo y funcionando!"

@app.route('/api/saludo')
def saludo():
    # Aquí podríamos consultar la base de datos que vayamos a conectar
    datos = {
        "mensaje": "Hola desde el Backend (Python)",
        "estudiante": "Tu Nombre",
        "estado": "Conexión Exitosa"
    }
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)