from flask import Flask, request, jsonify
from mysql.connector import pooling, Error
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Para comprimir respuestas y reducir latencia

# Pool de conexiones
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "gestion_inventario"
}
try:
    pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **dbconfig)
    print("✅ Pool de conexiones creado correctamente")
except Error as e:
    print(f"❌ Error al crear el pool de conexiones: {e}")

def get_db_connection():
    return pool.get_connection()

# Ruta raíz
@app.route('/')
def inicio():
    return '¡HOLIS!'

# Obtener todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nombre, precio, categoria_id FROM producto')
        productos = cursor.fetchall()
        return jsonify(productos)
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

# Agregar un nuevo producto
@app.route('/productos', methods=['POST'])
def agregar_producto():
    if not request.is_json:
        return jsonify({'error': 'El contenido debe ser JSON'}), 400
    data = request.get_json()
    try:
        nombre = data['nombre']
        descripcion = data['descripcion']
        cantidad = data['cantidad']
        precio = data['precio']
        categoria_id = data['categoria_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO producto (nombre, descripcion, cantidad, precio, categoria_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nombre, descripcion, cantidad, precio, categoria_id))
        conn.commit()
        return jsonify({'mensaje': 'Producto agregado'}), 201

    except KeyError as ke:
        return jsonify({'error': f'Falta el campo: {ke}'}), 400
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

# Obtener productos por categoría con paginación
@app.route('/productos/categoria/<int:categoria_id>', methods=['GET'])
def obtener_productos_por_categoria(categoria_id):
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        if page <= 0:
            return jsonify({'error': 'El parámetro page debe ser mayor que 0'}), 400
        if per_page <= 0 or per_page > 50:
            return jsonify({'error': 'El parámetro per_page debe estar entre 1 y 50'}), 400

        offset = (page - 1) * per_page

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Productos filtrados
        cursor.execute('''
            SELECT id, nombre, precio, categoria_id
            FROM producto
            WHERE categoria_id = %s
            LIMIT %s OFFSET %s
        ''', (categoria_id, per_page, offset))
        productos = cursor.fetchall()

        # Total de productos en esa categoría
        cursor.execute('SELECT COUNT(*) as total FROM producto WHERE categoria_id = %s', (categoria_id,))
        total = cursor.fetchone()['total']

        return jsonify({
            'productos': productos,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Error as e:
        return jsonify({'error': f'Error de base de datos: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

# Iniciar el servidor Flask
if __name__ == '__main__':
    # Fuerza a Flask a escuchar en 0.0.0.0:5000 (todas las interfaces IPv4)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
